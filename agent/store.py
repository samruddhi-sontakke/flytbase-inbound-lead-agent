"""Everything the agent writes goes through here: inbox log, leads, sources, stage outputs, trace, reports.

The leaddesk MCP server (leaddesk_mcp/server.py) exposes these functions as tools to Claude Code.
The web app (app/server.py) reads the same MongoDB documents.

Collections (database `flytbase_leads` by default):
    leads       one document per lead: status, events (live log), result.<stage>, summary, crm
    sources     one document per source per lead: id S#, url, title, raw text, kind, query
    inbox_log   one document per Gmail message the agent swept: deterministic markers + the agent's verdict
    agent_state single document `agent`: last tick, last inbox sweep, counters
"""
import datetime
import json
import re
import time

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app import db

from . import config, report
from .sources import Sources
from .stages import s1_qualify, s2_research, s3_emails, s4_case_study, s5_partner, s6_handoff

STAGE_FILES = [("lead", "0_lead"), ("qualification", "1_qualification"), ("research", "2_research"),
               ("emails", "3_emails"), ("case_study", "4_case_study"), ("partner", "5_partner"),
               ("handoff", "6_handoff")]
RUN_ORDER = ["lead", "qualification", "research", "case_study", "partner", "emails", "handoff"]
STAGE_NUM = {"qualification": 1, "research": 2, "emails": 3, "case_study": 4, "partner": 5, "handoff": 6}
STAGE_TITLE = {1: "Qualification", 2: "Deep account research", 3: "Response generation",
               4: "Case study matching", 5: "Partner identification", 6: "AE handoff"}


class StageError(ValueError):
    """Raised when a subagent's output is missing what the PDF requires; the message goes back to the agent."""


def now():
    return db.now()


def _lead(lead_id, proj=None):
    doc = db.leads().find_one({"_id": lead_id}, proj)
    if not doc:
        raise StageError(f"No lead with id {lead_id}")
    return doc


# ---------------------------------------------------------------- summaries for the lead list

def summarize(result):
    result = result or {}
    lead = result.get("lead") or {}
    c, co = lead.get("contact") or {}, lead.get("company") or {}
    scores = (result.get("qualification") or {}).get("scores") or {}
    partner = result.get("partner") or {}
    handoff = result.get("handoff") or {}
    tier_label = scores.get("priority_tier") or ""
    m = re.match(r"\s*(P\d)", tier_label)
    return {
        "name": c.get("name"), "email": c.get("email"), "title": c.get("title"), "division": c.get("division"),
        "seniority": c.get("seniority"),
        "company": co.get("short_name") or co.get("name"), "company_full": co.get("name"),
        "country": co.get("country"), "region": co.get("region"), "industry": co.get("industry"),
        "sub_industry": co.get("sub_industry"), "subject": lead.get("subject"), "referral": lead.get("referral_source"),
        "icp": scores.get("icp_fit_score"), "completeness": scores.get("meddpicc_completeness"),
        "priority": scores.get("priority_score"), "tier": m.group(1) if m else None, "tier_label": tier_label,
        "motion": partner.get("motion"),
        "partners": [p.get("name") for p in partner.get("recommended_partners") or [] if p.get("name")],
        "one_line": handoff.get("one_line_summary"),
    }


def guess_contact(email_text):
    """Quick name/company for the list before Stage 1 has run (regex, no AI)."""
    out = {}
    for key, pat in (("name", r"From:\s*([^(<\n]+)"), ("company", r"Company:\s*([^\n,]+)"), ("subject", r"Subject:\s*([^\n]+)")):
        m = re.search(pat, email_text or "")
        if m:
            out[key] = m.group(1).strip()
    return out


# ---------------------------------------------------------------- agent heartbeat

def record_tick(kind="tick", note=""):
    db.get_db().agent_state.update_one({"_id": "agent"}, {"$set": {f"last_{kind}": now(), f"last_{kind}_note": note[:300]},
                                                          "$inc": {f"count_{kind}": 1}}, upsert=True)
    return {"ok": True, "kind": kind}


def agent_state():
    return db.get_db().agent_state.find_one({"_id": "agent"}) or {}


# ---------------------------------------------------------------- inbox (Gmail) intake

FORM_MARKERS = {
    "contact_form_source": (r"flytbase\.com/contact", 4),
    "from_field": (r"^\s*From:\s*\S", 1),
    "title_field": (r"^\s*Title:\s*\S", 1),
    "company_field": (r"^\s*Company:\s*\S", 1),
    "subject_field": (r"^\s*Subject:\s*\S", 1),
    "context_field": (r"^\s*(Context|Message):\s*\S", 1),
    "buying_intent": (r"\b(drone|inspection|autonom|dock|bvlos|surveillance|monitoring|pilot|quote|pricing|demo)\w*", 2),
}
FREE_MAIL = re.compile(r"@(gmail|yahoo|hotmail|outlook|live|icloud|proton)\.", re.I)
NEWSLETTER = re.compile(r"\b(unsubscribe|newsletter|no-reply|noreply|do not reply|view in browser)\b", re.I)


def _markers(sender, subject, body):
    text = f"Subject: {subject}\n{body}"
    hits, score = {}, 0
    for name, (pat, pts) in FORM_MARKERS.items():
        ok = bool(re.search(pat, text, re.I | re.M))
        hits[name] = ok
        score += pts if ok else 0
    addr = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", f"{body} {sender}")
    hits["business_email_domain"] = bool(addr) and not FREE_MAIL.search(addr.group(0))
    score += 1 if hits["business_email_domain"] else 0
    hits["looks_like_bulk_mail"] = bool(NEWSLETTER.search(body or ""))
    score -= 3 if hits["looks_like_bulk_mail"] else 0
    return hits, score


def inbox_known(message_ids):
    found = {d["_id"] for d in db.get_db().inbox_log.find({"_id": {"$in": list(message_ids)}}, {"_id": 1})}
    return {"already_processed": sorted(found), "new": [m for m in message_ids if m not in found]}


def inbox_check(message_id, thread_id, sender, subject, body, received_at=""):
    """Deterministic first pass over one unread email. The agent then gives its own verdict."""
    col = db.get_db().inbox_log
    old = col.find_one({"_id": message_id})
    if old and old.get("verdict"):
        return {"already_processed": True, "verdict": old["verdict"], "lead_id": old.get("lead_id")}
    hits, score = _markers(sender, subject, body)
    hint = "likely_lead" if score >= 6 else "possible_lead" if score >= 3 else "unlikely_lead"
    col.update_one({"_id": message_id}, {"$set": {
        "thread_id": thread_id, "sender": sender, "subject": subject, "body": (body or "")[:20000],
        "received_at": received_at, "checked_at": now(), "markers": hits, "marker_score": score, "hint": hint}},
        upsert=True)
    return {"message_id": message_id, "marker_score": score, "hint": hint, "markers": hits,
            "rule": "score >= 6 likely lead, 3-5 possible, < 3 unlikely; the agent decides and records a reason"}


def inbox_check_batch(messages):
    """inbox_check for many messages at once (subject + snippet triage). Each item needs message_id, thread_id,
    sender, subject and body (the snippet is fine); received_at is optional."""
    out = []
    for m in messages or []:
        r = inbox_check(m.get("message_id"), m.get("thread_id"), m.get("sender", ""), m.get("subject", ""),
                        m.get("body") or m.get("snippet") or "", m.get("received_at", ""))
        out.append({"message_id": m.get("message_id"), "thread_id": m.get("thread_id"), "subject": m.get("subject"),
                    **{k: r.get(k) for k in ("already_processed", "verdict", "hint", "marker_score")}})
    return out


def inbox_verdicts(items):
    return [inbox_verdict(i.get("message_id"), bool(i.get("is_lead")), i.get("reason", "")) for i in items or []]


def inbox_verdict(message_id, is_lead, reason):
    col = db.get_db().inbox_log
    entry = col.find_one({"_id": message_id})
    if not entry:
        raise StageError("Run inbox_check on this message first")
    if entry.get("lead_id"):
        return {"lead_id": entry["lead_id"], "already_created": True}
    lead_id = None
    if is_lead:
        text = entry.get("body") or ""
        if "Subject:" not in text and entry.get("subject"):
            text = f"Subject: {entry['subject']}\n{text}"
        lead_id = create_lead(text, source="gmail", extra={
            "gmail": {"message_id": message_id, "thread_id": entry.get("thread_id"), "sender": entry.get("sender"),
                      "received_at": entry.get("received_at")}})
    col.update_one({"_id": message_id}, {"$set": {"verdict": "lead" if is_lead else "not_a_lead",
                                                  "reason": (reason or "")[:1000], "decided_at": now(), "lead_id": lead_id}})
    return {"message_id": message_id, "verdict": "lead" if is_lead else "not_a_lead", "lead_id": lead_id}


def inbox_list(limit=200):
    return list(db.get_db().inbox_log.find({}, {"body": 0}).sort("checked_at", -1).limit(limit))


# ---------------------------------------------------------------- leads and the queue

def create_lead(email_text, source="web", extra=None):
    lead_id = str(ObjectId())
    doc = {"_id": lead_id, "created_at": now(), "status": "queued", "source": source, "email_text": email_text,
           "summary": guess_contact(email_text), "stages_done": [], "events": [], "result": {}, "source_seq": 0,
           "crm": {"status": "new", "owner": "", "notes": []}}
    doc.update(extra or {})
    try:
        db.leads().insert_one(doc)
    except DuplicateKeyError:
        old = db.leads().find_one({"gmail.message_id": (extra or {}).get("gmail", {}).get("message_id")}, {"_id": 1})
        return old["_id"] if old else None
    return lead_id


def queue_status():
    docs = db.leads().find({"status": {"$in": ["queued", "running"]}},
                           {"status": 1, "summary": 1, "created_at": 1, "source": 1, "stage": 1, "lease_until": 1}).sort("created_at", 1)
    return [{"lead_id": d["_id"], "status": d["status"], "source": d.get("source"), "stage": d.get("stage"),
             "name": (d.get("summary") or {}).get("name"), "company": (d.get("summary") or {}).get("company")} for d in docs]


def claim_next():
    """Atomically claim the oldest queued lead, one lead at a time (lease lock)."""
    t = now()
    running = db.leads().find_one({"status": "running", "lease_until": {"$gt": t}}, {"_id": 1})
    if running:
        return {"claimed": None, "reason": f"lead {running['_id']} is still running"}
    db.leads().update_many({"status": "running", "lease_until": {"$lte": t}},
                           {"$set": {"status": "failed", "error": "Abandoned: the agent stopped before finishing (lease expired)."}})
    started = datetime.datetime.now()
    run_dir = config.OUTPUT_DIR / started.strftime("run_%Y-%m-%d_%H-%M-%S")
    doc = db.leads().find_one_and_update(
        {"status": "queued"},
        {"$set": {"status": "running", "started_at": t, "lease_until": t + datetime.timedelta(minutes=config.LEASE_MINUTES),
                  "run_dir": run_dir.relative_to(config.ROOT).as_posix(), "stage": None, "stages_done": [], "events": [],
                  "result": {}, "drafts": {}, "work": {}, "error": None, "source_seq": 0}},
        sort=[("created_at", 1)], return_document=ReturnDocument.AFTER)
    if not doc:
        return {"claimed": None, "reason": "queue is empty"}
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "input.txt").write_text(doc["email_text"], encoding="utf-8")
    db.get_db().sources.delete_many({"lead_id": doc["_id"]})
    progress(doc["_id"], f"Agent claimed this lead (source: {doc.get('source')})", "ok")
    return {"claimed": doc["_id"], "source": doc.get("source"), "run_dir": doc["run_dir"], "email_text": doc["email_text"]}


def _elapsed(doc):
    s = doc.get("started_at")
    return round((now() - s).total_seconds(), 1) if s else None


def progress(lead_id, message, kind="step", stage=None):
    doc = _lead(lead_id, {"started_at": 1})
    kind = kind if kind in ("stage", "step", "ok", "warn") else "step"
    upd = {"$set": {"lease_until": now() + datetime.timedelta(minutes=config.LEASE_MINUTES)}}
    if kind == "stage":
        num = int(stage) if stage else 0
        message = f"{num}|{message or STAGE_TITLE.get(num, '')}"
        key = next((k for k, v in STAGE_NUM.items() if v == num), None)
        upd["$set"]["stage"] = key
    upd["$push"] = {"events": {"t": _elapsed(doc), "kind": kind, "msg": str(message)[:600]}}
    db.leads().update_one({"_id": lead_id}, upd)
    return {"ok": True}


def get_lead(lead_id, keys=None):
    doc = _lead(lead_id, {"result": 1, "drafts": 1, "email_text": 1, "status": 1, "work": 1})
    res = doc.get("result") or {}
    out = {"lead_id": lead_id, "status": doc.get("status"), "email_text": doc.get("email_text")}
    for k in keys or RUN_ORDER:
        out[k] = res.get(k)
    if keys and "drafts" in keys:
        out["drafts"] = doc.get("drafts")
    return out


# ---------------------------------------------------------------- sources

def add_source(lead_id, url, title, content, kind="web", query=None, published=None):
    url = (url or "").strip()
    if not url:
        raise StageError("A source needs a URL")
    content = content or ""
    col = db.get_db().sources
    old = col.find_one({"lead_id": lead_id, "url": url})
    if old:
        if len(content) > len(old.get("content") or ""):
            col.update_one({"_id": old["_id"]}, {"$set": {"content": content}})
        return old["id"]
    seq = db.leads().find_one_and_update({"_id": lead_id}, {"$inc": {"source_seq": 1}}, {"source_seq": 1},
                                         return_document=ReturnDocument.AFTER)
    if not seq:
        raise StageError(f"No lead with id {lead_id}")
    sid = f"S{seq['source_seq']}"
    try:
        col.insert_one({"lead_id": lead_id, "id": sid, "url": url, "title": (title or url)[:200], "content": content,
                        "kind": kind, "query": query, "published": published, "added_at": now()})
    except DuplicateKeyError:  # the same URL registered by a parallel subagent a moment earlier
        return col.find_one({"lead_id": lead_id, "url": url})["id"]
    return sid


def get_source(lead_id, sid):
    return db.get_db().sources.find_one({"lead_id": lead_id, "id": sid}, {"_id": 0})


def list_sources(lead_id, with_content=False):
    proj = {"_id": 0, "lead_id": 0, "added_at": 0} if with_content else {"_id": 0, "lead_id": 0, "added_at": 0, "content": 0}
    docs = list(db.get_db().sources.find({"lead_id": lead_id}, proj))
    docs.sort(key=lambda s: int(s["id"][1:]))
    return docs


def _sources_obj(lead_id):
    s = Sources()
    for d in list_sources(lead_id, with_content=True):
        s.items[d["id"]] = d
        s._by_url[d["url"]] = d["id"]
    return s


# ---------------------------------------------------------------- trace

def _run_dir(lead_id):
    doc = _lead(lead_id, {"run_dir": 1})
    if not doc.get("run_dir"):
        raise StageError("This lead has not been claimed yet (no run folder)")
    return config.ROOT / doc["run_dir"]


def trace(lead_id, stage, agent, inputs, output, seconds=None, notes=""):
    """One line per subagent call, so anyone can see which agent definition ran on what and what it returned."""
    entry = {"at": now().isoformat(), "stage": stage, "model": "Claude Code subagent", "agent": agent,
             "system": f".claude/agents/{agent}.md" if agent else None, "prompt": inputs,
             "response": json.dumps(output, ensure_ascii=False) if not isinstance(output, str) else output,
             "seconds": seconds, "notes": notes}
    with open(_run_dir(lead_id) / "trace.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- stage outputs

def save_draft(lead_id, key, data):
    db.leads().update_one({"_id": lead_id}, {"$set": {f"drafts.{key}": data}})
    return {"ok": True, "saved": f"drafts.{key}"}


def save_work(lead_id, key, data):
    db.leads().update_one({"_id": lead_id}, {"$set": {f"work.{key}": data}})


def _kept_research_ids(research):
    ids = set()
    for _, f in s2_research._collect(research or {}):
        ids.update(f.get("source_ids") or [])
    for a in ((research or {}).get("positioning_recommendation") or {}).get("angles") or []:
        ids.update(re.findall(r"S\d+", str(a)))
    return ids


def _store_stage(lead_id, key, value, checklist=None):
    if checklist is not None:
        value["pdf_checklist"] = checklist
    rd = _run_dir(lead_id)
    name = dict(STAGE_FILES)[key]
    (rd / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    doc = _lead(lead_id, {"result": 1, "summary": 1})
    partial = dict(doc.get("result") or {})
    partial[key] = value
    summary = {**(doc.get("summary") or {}), **{k: v for k, v in summarize(partial).items() if v}}
    db.leads().update_one({"_id": lead_id}, {"$set": {f"result.{key}": value, "summary": summary},
                                             "$addToSet": {"stages_done": key}})


def save_stage(lead_id, stage, data, agent="", inputs="", seconds=None):
    """Validate a subagent's stage output, run the deterministic post-processing and the PDF checklist,
    store it (MongoDB + run folder) and return what Python computed so the agent can see it."""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise StageError(f"Stage output is not valid JSON: {e}")
    doc = _lead(lead_id, {"result": 1, "work": 1})
    res = doc.get("result") or {}
    out = {"stage": stage}

    if stage == "qualification":
        problems = s1_qualify.validate(data)
        if problems:
            raise StageError("Fix and resubmit: " + "; ".join(problems))
        q, lead = s1_qualify.postprocess(data)
        _store_stage(lead_id, "lead", lead)
        check = s1_qualify.checklist(q, lead)
        _store_stage(lead_id, "qualification", q, check)
        out.update(scores=q["scores"], known=q["known_information"], gaps=[m["element"] for m in q["missing_information"]])

    elif stage == "research":
        raise StageError("Research is saved by submit_fact_check after the fact-checker runs (save the brief with save_draft first).")

    elif stage == "case_study":
        work = (doc.get("work") or {}).get("case_study") or {}
        if not work:
            raise StageError("Run case_study_candidates first so the crawl and pre-scores are on record")
        data["pre_scores"] = work.get("scored")
        data["case_studies_scanned"] = work.get("scanned")
        data["prescore_inputs"] = work.get("inputs")
        primary = data.get("primary") or {}
        primary["url_verified"] = primary.get("url") in set(work.get("urls") or [])
        data["primary"] = primary
        if not primary.get("why_strongest_fit"):
            raise StageError("primary.why_strongest_fit is required")
        check = s4_case_study.checklist(data)
        _store_stage(lead_id, "case_study", data, check)
        out.update(primary=primary.get("title"), url_verified=primary["url_verified"])

    elif stage == "partner":
        if data.get("motion") not in s5_partner.MOTIONS:
            raise StageError(f"motion must be one of {s5_partner.MOTIONS}")
        text = " ".join((s.get("content") or "") + " " + (s.get("title") or "") for s in list_sources(lead_id, True))
        text += json.dumps(res.get("case_study") or {}, ensure_ascii=False)
        unverified = s5_partner.verify(data, text)
        check = s5_partner.checklist(data)
        _store_stage(lead_id, "partner", data, check)
        out.update(motion=data["motion"], unverified_partners=unverified)

    elif stage == "emails":
        if not res.get("qualification") or not res.get("research"):
            raise StageError("Stage 3 needs Stage 1 and Stage 2 saved first")
        problems = s3_emails.check_links(data, res["qualification"], _kept_research_ids(res["research"]))
        check = s3_emails.checklist(data)
        _store_stage(lead_id, "emails", data, check)
        out.update(emails=len(data.get("emails") or []), problems=problems)

    elif stage == "handoff":
        s6_handoff.check_highlights(data, _kept_research_ids(res.get("research")))
        check = s6_handoff.checklist(data)
        _store_stage(lead_id, "handoff", data, check)

    else:
        raise StageError(f"Unknown stage {stage!r}")

    trace(lead_id, stage, agent, inputs, data, seconds)
    out["pdf_checklist"] = check
    out["checklist_passed"] = all(c["ok"] for c in check)
    progress(lead_id, f"Saved {stage}: PDF checklist {sum(c['ok'] for c in check)}/{len(check)}",
             "ok" if out["checklist_passed"] else "warn")
    return out


def research_claims(lead_id):
    doc = _lead(lead_id, {"drafts": 1})
    brief = (doc.get("drafts") or {}).get("research")
    if not brief:
        raise StageError("No research draft saved yet")
    return s2_research.claims_for_check(brief, lambda i: get_source(lead_id, i))


def submit_fact_check(lead_id, verdicts, agent="research-fact-checker", seconds=None):
    doc = _lead(lead_id, {"drafts": 1})
    brief = (doc.get("drafts") or {}).get("research")
    if not brief:
        raise StageError("No research draft saved yet")
    if isinstance(verdicts, str):
        verdicts = json.loads(verdicts)
    brief = s2_research.apply_fact_check(brief, verdicts, lambda i: get_source(lead_id, i))
    brief["sources_registered"] = len(list_sources(lead_id))
    check = s2_research.checklist(brief)
    _store_stage(lead_id, "research", brief, check)
    trace(lead_id, "research_fact_check", agent, f"{len(verdicts)} verdicts", verdicts, seconds)
    passed = all(c["ok"] for c in check)
    progress(lead_id, f"Fact-check: {brief['fact_check']['claims_checked']} claims checked, "
                      f"{brief['fact_check']['removed']} removed. PDF checklist {sum(c['ok'] for c in check)}/{len(check)}",
             "ok" if passed else "warn")
    return {"fact_check": brief["fact_check"], "removed": [f.get("claim") for f in brief["removed_by_fact_check"]],
            "pdf_checklist": check, "checklist_passed": passed}


# ---------------------------------------------------------------- finish

def finish(lead_id):
    doc = _lead(lead_id)
    res = doc.get("result") or {}
    missing = [k for k in RUN_ORDER if not res.get(k)]
    if missing:
        raise StageError(f"Cannot finish: stages missing: {', '.join(missing)}")
    rd = _run_dir(lead_id)
    calls = sum(1 for _ in open(rd / "trace.jsonl", encoding="utf-8")) if (rd / "trace.jsonl").exists() else 0
    started = doc.get("started_at") or now()
    meta = {"started": started.astimezone().strftime("%Y-%m-%d %H:%M"), "seconds": round((now() - started).total_seconds()),
            "llm_calls": calls, "agent": "Claude Code (subagents per stage)", "input_file": doc.get("source")}
    result = {"meta": meta, **{k: res[k] for k in RUN_ORDER}}
    sources = _sources_obj(lead_id)
    (rd / "sources.json").write_text(json.dumps(sources.public_list(), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    md = report.build(result, sources)
    (rd / "REPORT.md").write_text(md, encoding="utf-8")
    (rd / "REPORT.html").write_text(report.to_html(md, "Inbound Lead Report"), encoding="utf-8")
    checks = {k: (res[k] or {}).get("pdf_checklist") for k in STAGE_NUM}
    passed = sum(c["ok"] for v in checks.values() for c in v or [])
    total = sum(len(v or []) for v in checks.values())
    db.leads().update_one({"_id": lead_id}, {"$set": {
        "status": "done", "finished_at": now(), "meta": meta, "summary": summarize(res), "stage": None,
        "sources": sources.public_list(), "pdf_checklist_score": f"{passed}/{total}"}, "$unset": {"lease_until": ""}})
    progress(lead_id, f"Done in {meta['seconds']}s: {calls} subagent calls, {len(sources.items)} sources, PDF checklist {passed}/{total}", "ok")
    return {"status": "done", "run_dir": doc["run_dir"], "seconds": meta["seconds"], "pdf_checklist": f"{passed}/{total}"}


def fail(lead_id, error):
    db.leads().update_one({"_id": lead_id}, {"$set": {"status": "failed", "finished_at": now(), "error": str(error)[:600]},
                                             "$unset": {"lease_until": ""},
                                             "$push": {"events": {"t": None, "kind": "warn", "msg": f"Stopped: {str(error)[:300]}"}}})
    return {"status": "failed"}
