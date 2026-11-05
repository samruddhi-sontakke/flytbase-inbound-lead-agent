"""A small demo CRM on top of the lead documents: team, routing (lead assignment), SLA, tasks, deals, accounts
and an audit trail. Everything here is plain, deterministic Python: no AI call, and nothing is ever sent.

Collections (same database as the leads):
    team          one document per person. The seeded people are DEMO placeholders (role-style names, demo: true).
    crm_config    `routing`: territories -> BDR pools, fallback pool, which tiers get an AE at once, SLA hours.
    crm_tasks     one per to-do: "send email N" for the BDR (from Stage 3) and the handoff call for the AE (Stage 6).
    crm_activity  append-only audit trail: assignments, reassignments, stage moves, tasks created/completed.

On the lead document the CRM keeps `crm.*`:
    status        the deal stage (one deal per lead); the old desk values are mapped by `stage_of`
    owner/owner_id the BDR, ae/ae_id the AE, assignment {rule, reason, by, at}, sla {tier, hours, start, due_at},
    first_response_at (set when the BDR marks email 1 as sent from their own mailbox)

How a lead is routed (`route`, a pure function, so it is unit-tested and shown in the UI's "explain"):
    1. Territory: the lead's sales region (Stage 1: LATAM, North America, EMEA, APAC) picks a BDR pool.
       No region, or no active BDR in that pool -> the fallback pool.
    2. Round-robin weighted by load: inside the pool, the BDR with the lowest open-load / capacity wins.
       People at capacity are skipped while anyone has room. Ties go to whoever was assigned longest ago.
    3. Tiers listed in `ae_tiers` (P1 by default) also get an AE straight away: AEs whose segments match the
       lead's industry first (same load rule), else the AE fallback pool.
    4. SLA: first response due `sla_hours[tier]` after the lead arrived (P1 1h, P2 24h, P3 72h by default).
"""
import datetime
import logging
import re
import threading

from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from app import db

log = logging.getLogger("leaddesk.crm")

STAGES = ["new", "contacted", "discovery", "meeting_booked", "handed_to_ae", "won", "lost", "nurture"]
STAGE_LABEL = {"new": "New", "contacted": "Contacted", "discovery": "Discovery", "meeting_booked": "Meeting booked",
               "handed_to_ae": "Handed to AE", "won": "Won", "lost": "Lost", "nurture": "Nurture"}
LEGACY_STAGE = {"working": "contacted", "handed_off": "handed_to_ae", "disqualified": "lost"}
OPEN_STAGES = {"new", "contacted", "discovery", "meeting_booked", "handed_to_ae"}
REGIONS = ["LATAM", "North America", "EMEA", "APAC"]
ROLES = ["BDR", "AE"]
FREE_MAIL = re.compile(r"^(gmail|googlemail|yahoo|hotmail|outlook|live|icloud|proton|protonmail|aol|gmx)\.", re.I)

DEMO_TEAM = [
    {"_id": "bdr-latam", "name": "BDR · LATAM (demo)", "role": "BDR", "region": "LATAM", "segments": [], "capacity": 25},
    {"_id": "bdr-latam-2", "name": "BDR · LATAM 2 (demo)", "role": "BDR", "region": "LATAM", "segments": [], "capacity": 20},
    {"_id": "bdr-na", "name": "BDR · North America (demo)", "role": "BDR", "region": "North America", "segments": [], "capacity": 30},
    {"_id": "bdr-emea", "name": "BDR · EMEA (demo)", "role": "BDR", "region": "EMEA", "segments": [], "capacity": 30},
    {"_id": "bdr-apac", "name": "BDR · APAC (demo)", "role": "BDR", "region": "APAC", "segments": [], "capacity": 25},
    {"_id": "ae-mining", "name": "AE · Mining & Energy (demo)", "role": "AE", "region": "Global",
     "segments": ["Mining", "Energy", "Oil & Gas", "Utilities", "Metals", "Solar", "Power"], "capacity": 12},
    {"_id": "ae-enterprise", "name": "AE · Enterprise (demo)", "role": "AE", "region": "Global", "segments": [], "capacity": 15},
]

DEFAULT_ROUTING = {
    "territories": {"LATAM": ["bdr-latam", "bdr-latam-2"], "North America": ["bdr-na"], "EMEA": ["bdr-emea"],
                    "APAC": ["bdr-apac"]},
    "fallback_pool": ["bdr-na", "bdr-emea"],
    "ae_tiers": ["P1"],
    "ae_fallback": ["ae-enterprise"],
    "sla_hours": {"P1": 1, "P2": 24, "P3": 72, "default": 24},
    "auto_assign": True,
}


def now():
    return db.now()


def _db():
    return db.get_db()


def _aware(v):
    if isinstance(v, datetime.datetime) and v.tzinfo is None:
        return v.replace(tzinfo=datetime.timezone.utc)
    return v


# ---------------------------------------------------------------- setup

def ensure():
    """Indexes, the demo team and the default routing config (only when missing, never overwritten)."""
    d = _db()
    d.crm_tasks.create_index([("lead_id", ASCENDING), ("key", ASCENDING)], unique=True)
    d.crm_tasks.create_index([("owner_id", ASCENDING), ("status", ASCENDING), ("due_at", ASCENDING)])
    d.crm_activity.create_index([("at", DESCENDING)])
    d.crm_activity.create_index([("lead_id", ASCENDING), ("at", DESCENDING)])
    if d.team.count_documents({}) == 0:
        t = now()
        for m in DEMO_TEAM:
            try:
                d.team.insert_one({**m, "active": True, "demo": True, "created_at": t, "last_assigned_at": None})
            except DuplicateKeyError:
                pass
    if not d.crm_config.find_one({"_id": "routing"}):
        try:
            d.crm_config.insert_one({"_id": "routing", **DEFAULT_ROUTING, "updated_at": now()})
        except DuplicateKeyError:
            pass


def routing_config():
    cfg = _db().crm_config.find_one({"_id": "routing"}) or {}
    out = {k: v for k, v in DEFAULT_ROUTING.items()}
    out.update({k: v for k, v in cfg.items() if k in DEFAULT_ROUTING})
    out["sla_hours"] = {**DEFAULT_ROUTING["sla_hours"], **(cfg.get("sla_hours") or {})}
    out["updated_at"] = cfg.get("updated_at")
    return out


def validate_routing(body, team_ids):
    """Return (clean config, problems). Unknown ids are rejected so a typo cannot silently empty a pool."""
    problems, clean = [], {}
    if "territories" in body:
        terr = body["territories"]
        if not isinstance(terr, dict):
            problems.append("territories must be an object {region: [member ids]}")
        else:
            clean["territories"] = {}
            for region, ids in terr.items():
                ids = [str(i) for i in (ids or [])]
                bad = [i for i in ids if i not in team_ids]
                if bad:
                    problems.append(f"unknown team ids in {region}: {', '.join(bad)}")
                clean["territories"][str(region)[:40]] = ids
    for key in ("fallback_pool", "ae_fallback"):
        if key in body:
            ids = [str(i) for i in (body[key] or [])]
            bad = [i for i in ids if i not in team_ids]
            if bad:
                problems.append(f"unknown team ids in {key}: {', '.join(bad)}")
            clean[key] = ids
    if "ae_tiers" in body:
        tiers = [str(t) for t in (body["ae_tiers"] or [])]
        if any(t not in ("P1", "P2", "P3") for t in tiers):
            problems.append("ae_tiers may only contain P1, P2, P3")
        clean["ae_tiers"] = tiers
    if "sla_hours" in body:
        sla = {}
        for k, v in (body["sla_hours"] or {}).items():
            try:
                h = float(v)
            except (TypeError, ValueError):
                problems.append(f"sla_hours.{k} must be a number")
                continue
            if h <= 0 or h > 24 * 30:
                problems.append(f"sla_hours.{k} must be between 0 and 720 hours")
            sla[str(k)] = h
        clean["sla_hours"] = sla
    if "auto_assign" in body:
        clean["auto_assign"] = bool(body["auto_assign"])
    return clean, problems


def save_routing(clean, actor="web"):
    clean = dict(clean)
    clean["updated_at"] = now()
    _db().crm_config.update_one({"_id": "routing"}, {"$set": clean}, upsert=True)
    log_activity(None, "routing_changed", f"Routing rules updated: {', '.join(k for k in clean if k != 'updated_at')}",
                 actor, {k: v for k, v in clean.items() if k != "updated_at"})
    return routing_config()


# ---------------------------------------------------------------- team

def team(active_only=False):
    q = {"active": True} if active_only else {}
    return list(_db().team.find(q).sort([("role", ASCENDING), ("_id", ASCENDING)]))


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:40] or "member"


def clean_member(body, partial=False):
    out, problems = {}, []
    if "name" in body or not partial:
        name = str(body.get("name") or "").strip()[:80]
        if not name:
            problems.append("name is required")
        out["name"] = name
    if "role" in body or not partial:
        role = str(body.get("role") or "BDR").upper()
        if role not in ROLES:
            problems.append("role must be BDR or AE")
        out["role"] = role
    if "region" in body or not partial:
        out["region"] = str(body.get("region") or "Global").strip()[:40]
    if "segments" in body:
        segs = body["segments"]
        if isinstance(segs, str):
            segs = [s.strip() for s in segs.split(",")]
        out["segments"] = [str(s).strip()[:40] for s in segs or [] if str(s).strip()]
    elif not partial:
        out["segments"] = []
    if "capacity" in body or not partial:
        try:
            cap = int(body.get("capacity") if body.get("capacity") is not None else 20)
        except (TypeError, ValueError):
            cap = -1
        if cap < 1 or cap > 500:
            problems.append("capacity must be a whole number from 1 to 500")
        out["capacity"] = cap
    if "active" in body:
        out["active"] = bool(body["active"])
    return out, problems


def create_member(fields, actor="web"):
    base = _slug(f"{fields['role']}-{fields['name']}")
    mid, n = base, 1
    while _db().team.find_one({"_id": mid}):
        n += 1
        mid = f"{base}-{n}"
    doc = {"_id": mid, **fields, "active": fields.get("active", True), "demo": False, "created_at": now(),
           "last_assigned_at": None}
    _db().team.insert_one(doc)
    # a new BDR joins the pool of their region, so routing can use them at once
    if doc["role"] == "BDR" and doc["region"] in REGIONS:
        _db().crm_config.update_one({"_id": "routing"}, {"$addToSet": {f"territories.{doc['region']}": mid}})
    log_activity(None, "team_changed", f"Added {doc['name']} ({doc['role']}, {doc['region']}, capacity {doc['capacity']})", actor)
    return doc


def update_member(mid, fields, actor="web"):
    doc = _db().team.find_one_and_update({"_id": mid}, {"$set": fields}, return_document=ReturnDocument.AFTER)
    if doc:
        log_activity(None, "team_changed", f"Updated {doc['name']}: {', '.join(f'{k}={v}' for k, v in fields.items())}", actor)
    return doc


def loads(exclude_lead=None):
    """Open load per person: leads in an open deal stage where they are the BDR (owner_id) or the AE (ae_id)."""
    out = {}
    q = {"archived": {"$ne": True}, "crm.assignment": {"$exists": True}}
    for d in db.leads().find(q, {"crm": 1}):
        if d["_id"] == exclude_lead:
            continue
        c = d.get("crm") or {}
        if stage_of(c.get("status")) not in OPEN_STAGES:
            continue
        for key in ("owner_id", "ae_id"):
            if c.get(key):
                out[c[key]] = out.get(c[key], 0) + 1
    return out


# ---------------------------------------------------------------- routing (pure)

def _pick(ids, members, load):
    """Lowest load/capacity wins; people at capacity only when everyone is; ties -> assigned longest ago, then id."""
    cands = []
    for i in ids:
        m = members.get(i)
        if not m:
            continue
        cap = max(1, int(m.get("capacity") or 1))
        n = load.get(i, 0)
        last = _aware(m.get("last_assigned_at"))
        cands.append({"id": i, "name": m.get("name"), "open": n, "capacity": cap, "ratio": round(n / cap, 4),
                      "at_capacity": n >= cap, "last_assigned_at": last.isoformat() if last else None})
    if not cands:
        return None, []
    room = [c for c in cands if not c["at_capacity"]] or cands
    epoch = "0000"
    best = min(room, key=lambda c: (c["ratio"], c["last_assigned_at"] or epoch, c["id"]))
    for c in cands:
        c["picked"] = c["id"] == best["id"]
    return best, cands


def _fmt(c):
    return f"{c['name']} ({c['open']}/{c['capacity']} open)"


def route(summary, members, load, cfg):
    """Decide BDR (and AE if the tier needs one) for a lead summary. Pure: returns the decision and its reasons."""
    summary = summary or {}
    by_id = {m["_id"]: m for m in members if m.get("active", True)}
    bdrs = {i: m for i, m in by_id.items() if m.get("role") == "BDR"}
    aes = {i: m for i, m in by_id.items() if m.get("role") == "AE"}
    region, tier = summary.get("region"), summary.get("tier")
    industry = " ".join(str(summary.get(k) or "") for k in ("industry", "sub_industry")).strip()
    steps = []

    pool = [i for i in (cfg.get("territories") or {}).get(region or "", []) if i in bdrs]
    if pool:
        rule = f"territory:{region}"
        steps.append(f"Region {region} -> {region} territory pool ({len(pool)} active BDR{'s' if len(pool) != 1 else ''}).")
    else:
        pool = [i for i in cfg.get("fallback_pool") or [] if i in bdrs] or sorted(bdrs)
        rule = "fallback_pool"
        why = "no region on the lead" if not region else f"no active BDR in the {region} territory"
        steps.append(f"Fallback pool: {why}.")
    owner, owner_cands = _pick(pool, bdrs, load)
    if owner:
        tie = sum(1 for c in owner_cands if c["ratio"] == owner["ratio"] and not c["at_capacity"]) > 1
        steps.append(f"BDR: {_fmt(owner)}, lowest open load for capacity"
                     + ("; tie broken by who was assigned longest ago." if tie else "."))
    else:
        steps.append("BDR: nobody active to assign.")

    ae, ae_cands, ae_rule = None, [], None
    if tier and tier in (cfg.get("ae_tiers") or []):
        low = industry.lower()
        match = [i for i, m in aes.items() if low and any(s.lower() in low for s in m.get("segments") or [])]
        if match:
            ae, ae_cands = _pick(match, aes, load)
            seg = next(s for s in aes[ae["id"]].get("segments") or [] if s.lower() in low)
            ae_rule = f"segment:{seg}"
            steps.append(f"{tier} gets an AE at once: industry '{industry}' matches segment '{seg}' -> {_fmt(ae)}.")
        else:
            fb = [i for i in cfg.get("ae_fallback") or [] if i in aes] or sorted(aes)
            ae, ae_cands = _pick(fb, aes, load)
            ae_rule = "ae_fallback"
            steps.append(f"{tier} gets an AE at once: no segment matches '{industry or 'unknown industry'}', "
                         f"AE fallback -> {_fmt(ae) if ae else 'nobody active'}.")
    else:
        steps.append(f"No AE yet: {tier or 'unscored'} is not in the tiers that get an AE at once "
                     f"({', '.join(cfg.get('ae_tiers') or []) or 'none'}); the AE is added at handoff.")
    hours = sla_hours(tier, cfg)
    steps.append(f"SLA: first response within {_hours_text(hours)} ({tier or 'default'}).")
    return {"owner": owner, "owner_candidates": owner_cands, "ae": ae, "ae_candidates": ae_cands,
            "rule": rule + (f" + {ae_rule}" if ae_rule else ""), "reason": " ".join(steps), "steps": steps,
            "sla_hours": hours, "inputs": {"region": region, "tier": tier, "industry": industry}}


# ---------------------------------------------------------------- SLA

def sla_hours(tier, cfg):
    h = cfg.get("sla_hours") or {}
    return float(h.get(tier) or h.get("default") or 24)


def _hours_text(h):
    if h < 1:
        return f"{round(h * 60)} min"
    if h % 24 == 0 and h >= 24:
        return f"{int(h // 24)} day{'s' if h >= 48 else ''} ({int(h)}h)"
    return f"{h:g}h"


def sla_state(crm, at=None):
    """met / breached / open (with seconds left) / none, from crm.sla.due_at and crm.first_response_at."""
    crm = crm or {}
    sla = crm.get("sla") or {}
    due = _aware(sla.get("due_at"))
    if not due:
        return {"state": "none"}
    at = at or now()
    first = _aware(crm.get("first_response_at"))
    base = {"due_at": due, "hours": sla.get("hours"), "tier": sla.get("tier")}
    if first:
        return {**base, "state": "met" if first <= due else "breached", "responded_at": first,
                "late_by_seconds": max(0, round((first - due).total_seconds()))}
    left = round((due - at).total_seconds())
    if stage_of(crm.get("status")) in ("lost", "nurture", "won"):
        return {**base, "state": "closed", "seconds_left": left}
    return {**base, "state": "open" if left >= 0 else "breached", "seconds_left": left, "overdue": left < 0}


# ---------------------------------------------------------------- tasks from the stage outputs

_UNIT = [(r"business\s+days?|working\s+days?", 86400), (r"weeks?|wks?", 604800), (r"days?|d\b", 86400),
         (r"hours?|hrs?|h\b", 3600), (r"minutes?|mins?|m\b", 60)]


def parse_offset(text, default_hours=24.0):
    """Turn a stage's free-text timing ("Within 1 hour", "3 days after no reply", "Day 7", "Same business day")
    into (seconds, chained, rule). chained=True means "after the previous step", else after the lead arrived."""
    t = (text or "").lower().strip()
    chained = bool(re.search(r"\bafter\b", t)) and not re.search(r"after (the )?(inbound|form|enquiry|inquiry|lead)", t)
    m = re.search(r"\bday\s*(\d+)\b", t)
    if m:
        return int(m.group(1)) * 86400, False, f"day {m.group(1)} after the lead arrived"
    for pat, sec in _UNIT:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:-\s*\d+\s*)?(" + pat + ")", t)
        if m:
            n = float(m.group(1))
            return round(n * sec), chained, f"{m.group(1)} {m.group(2)} {'after the previous step' if chained else 'after the lead arrived'}"
    words = [(r"immediate|asap|right away|now\b", 0.25), (r"within (the|an|one) hour|an hour", 1),
             (r"same (business )?day|today|end of day|eod", 8), (r"next (business |working )?day|tomorrow", 24),
             (r"(a|one) week", 168), (r"two weeks|fortnight", 336)]
    for pat, h in words:
        if re.search(pat, t):
            return round(h * 3600), chained, f"'{text}' read as {h:g}h {'after the previous step' if chained else 'after the lead arrived'}"
    return round(default_hours * 3600), chained, f"no timing found in '{text}', default {default_hours:g}h"


def plan_tasks(lead, owner, ae, start):
    """Tasks the lead's stage outputs imply. Pure (no DB): returns task dicts keyed by `key` (idempotent)."""
    res = lead.get("result") or {}
    emails = sorted(((res.get("emails") or {}).get("emails") or []), key=lambda e: int(e.get("step") or 0))
    out, prev = [], start
    for i, e in enumerate(emails):
        step = int(e.get("step") or i + 1)
        sec, chained, rule = parse_offset(e.get("send_when"), default_hours=1 if step == 1 else 72)
        due = (prev if chained else start) + datetime.timedelta(seconds=sec)
        prev = due
        out.append({"key": f"email-{step}", "kind": "email", "step": step,
                    "title": f"Send email {step}" + (f": {e.get('subject')}" if e.get("subject") else ""),
                    "detail": "Review the draft on the lead page and send it from your own mailbox. The desk never sends."
                              + (" Skip it if the buyer has replied." if step > 1 else ""),
                    "owner_id": owner["id"] if owner else None, "owner_name": owner["name"] if owner else None,
                    "due_at": due, "due_rule": f"send_when '{e.get('send_when')}': {rule}"})
    ns = (res.get("handoff") or {}).get("suggested_next_step") or {}
    if ns.get("action"):
        sec, _, rule = parse_offset(ns.get("by_when"), default_hours=24)
        who = ae or owner
        out.append({"key": "handoff", "kind": "call", "step": None, "title": f"Handoff call: {ns['action']}"[:240],
                    "detail": (ns.get("rationale") or "")[:600] + ("" if ae else " (No AE assigned yet: the BDR holds it until handoff.)"),
                    "owner_id": who["id"] if who else None, "owner_name": who["name"] if who else None,
                    "owner_role": "AE" if ae else "BDR",
                    "due_at": start + datetime.timedelta(seconds=sec), "due_rule": f"by_when '{ns.get('by_when')}': {rule}"})
    return out


def _start_of(lead):
    return _aware(lead.get("created_at")) or now()


def ensure_tasks(lead, owner, ae, actor="auto"):
    created = []
    for t in plan_tasks(lead, owner, ae, _start_of(lead)):
        doc = {"_id": f"{lead['_id']}:{t['key']}", "lead_id": lead["_id"], "status": "open", "created_at": now(),
               "created_by": actor, **t}
        try:
            _db().crm_tasks.insert_one(doc)
            created.append(doc)
        except DuplicateKeyError:
            pass
    if created:
        log_activity(lead["_id"], "tasks_created", f"{len(created)} task(s) created from the stage outputs: "
                     + "; ".join(f"{t['title'][:60]} -> {t['owner_name'] or 'unassigned'}" for t in created), actor)
    return created


def tasks(owner_id=None, status="open", lead_id=None, limit=500):
    q = {}
    if owner_id:
        q["owner_id"] = owner_id
    if status in ("open", "done"):
        q["status"] = status
    if lead_id:
        q["lead_id"] = lead_id
    out = list(_db().crm_tasks.find(q).sort([("status", DESCENDING), ("due_at", ASCENDING)]).limit(limit))
    t = now()
    for x in out:
        due = _aware(x.get("due_at"))
        x["overdue"] = x.get("status") == "open" and bool(due) and due < t
    if out:
        names = {d["_id"]: d.get("summary") or {} for d in db.leads().find({"_id": {"$in": list({x["lead_id"] for x in out})}},
                                                                        {"summary": 1})}
        for x in out:
            s = names.get(x["lead_id"]) or {}
            x["lead"] = {"name": s.get("name"), "company": s.get("company"), "tier": s.get("tier")}
    return out


def complete_task(task_id, actor="web", note=""):
    t = _db().crm_tasks.find_one_and_update({"_id": task_id, "status": "open"},
                                            {"$set": {"status": "done", "done_at": now(), "done_by": actor,
                                                      "done_note": (note or "")[:500]}},
                                            return_document=ReturnDocument.AFTER)
    if not t:
        return None
    log_activity(t["lead_id"], "task_done", f"Done: {t['title'][:120]}" + (f" ({note[:120]})" if note else ""), actor)
    if t.get("key") == "email-1":
        lead = db.leads().find_one({"_id": t["lead_id"]}, {"crm": 1}) or {}
        c = lead.get("crm") or {}
        if not c.get("first_response_at"):
            db.leads().update_one({"_id": t["lead_id"]}, {"$set": {"crm.first_response_at": t["done_at"]}})
            st = sla_state({**c, "first_response_at": t["done_at"]})
            log_activity(t["lead_id"], "first_response", f"First response recorded: SLA {st['state']}", actor)
        if stage_of(c.get("status")) == "new":
            set_stage(t["lead_id"], "contacted", actor, "email 1 marked as sent")
    return t


def add_task(lead_id, title, owner_id, due_at, actor="web"):
    m = _db().team.find_one({"_id": owner_id}) if owner_id else None
    key = f"manual-{int(now().timestamp() * 1000)}"
    doc = {"_id": f"{lead_id}:{key}", "lead_id": lead_id, "key": key, "kind": "manual", "step": None, "title": title[:240],
           "detail": "", "owner_id": m["_id"] if m else None, "owner_name": m["name"] if m else None, "due_at": due_at,
           "due_rule": "set by hand", "status": "open", "created_at": now(), "created_by": actor}
    _db().crm_tasks.insert_one(doc)
    log_activity(lead_id, "tasks_created", f"Task added: {title[:120]} -> {doc['owner_name'] or 'unassigned'}", actor)
    return doc


# ---------------------------------------------------------------- assignment

def _member_ref(m):
    return {"id": m["_id"], "name": m["name"]} if m else None


def assign(lead_id, actor="auto", owner_id=None, ae_id=None, reason=None, only_if_unassigned=False):
    """Route (or hand-pick) the BDR/AE, set the SLA, write the audit entry, create/move tasks.
    Returns the decision, or None when `only_if_unassigned` and someone else got there first."""
    lead = db.leads().find_one({"_id": lead_id})
    if not lead:
        raise KeyError(lead_id)
    cfg = routing_config()
    members = team()
    by_id = {m["_id"]: m for m in members}
    old = lead.get("crm") or {}
    decision = route(lead.get("summary") or {}, members, loads(exclude_lead=lead_id), cfg)
    manual = owner_id is not None or ae_id is not None
    if manual:
        for mid, role in ((owner_id, "BDR"), (ae_id, "AE")):
            if mid and (mid not in by_id or by_id[mid].get("role") != role):
                raise ValueError(f"{mid} is not a {role} on the team")
        owner = by_id.get(owner_id) if owner_id else by_id.get(old.get("owner_id"))
        ae = by_id.get(ae_id) if ae_id else by_id.get(old.get("ae_id"))
        if ae_id == "":
            ae = None
        rule = "manual"
        why = (reason or "").strip() or "reassigned by hand"
        text = f"Reassigned by {actor}: {why}"
    else:
        owner = by_id.get(decision["owner"]["id"]) if decision["owner"] else None
        ae = by_id.get(decision["ae"]["id"]) if decision["ae"] else by_id.get(old.get("ae_id"))
        rule, text = decision["rule"], decision["reason"]
        if reason:
            text = f"{reason.strip()} {text}"
    t = now()
    tier = (lead.get("summary") or {}).get("tier")
    start = _start_of(lead)
    sets = {"crm.owner": owner["name"] if owner else "", "crm.owner_id": owner["_id"] if owner else None,
            "crm.ae": ae["name"] if ae else "", "crm.ae_id": ae["_id"] if ae else None,
            "crm.assignment": {"rule": rule, "reason": text, "by": actor, "at": t,
                               "candidates": decision["owner_candidates"], "ae_candidates": decision["ae_candidates"]},
            "crm.updated_at": t}
    if not old.get("sla") or old.get("sla", {}).get("tier") != tier:
        hours = sla_hours(tier, cfg)
        sets["crm.sla"] = {"tier": tier, "hours": hours, "start": start, "due_at": start + datetime.timedelta(hours=hours)}
    if not old.get("status") or old.get("status") not in STAGES:
        sets["crm.status"] = stage_of(old.get("status"))
    filt = {"_id": lead_id}
    if only_if_unassigned:
        filt["crm.assignment"] = {"$exists": False}
    if not db.leads().find_one_and_update(filt, {"$set": sets}):
        return None
    for m in (owner, ae):
        if m and m["_id"] not in (old.get("owner_id"), old.get("ae_id")):
            _db().team.update_one({"_id": m["_id"]}, {"$set": {"last_assigned_at": t}})
    kind = "reassigned" if old.get("assignment") else "assigned"
    who = f"BDR {owner['name'] if owner else 'none'}" + (f", AE {ae['name']}" if ae else "")
    log_activity(lead_id, kind, f"{who}. {text}", actor, {"rule": rule, "owner_id": sets["crm.owner_id"], "ae_id": sets["crm.ae_id"],
                                                         "previous": {"owner_id": old.get("owner_id"), "ae_id": old.get("ae_id")}})
    # move open tasks to the new people, then create any missing ones
    if old.get("owner_id") and owner and old.get("owner_id") != owner["_id"]:
        _db().crm_tasks.update_many({"lead_id": lead_id, "status": "open", "owner_id": old["owner_id"], "kind": "email"},
                                    {"$set": {"owner_id": owner["_id"], "owner_name": owner["name"]}})
    if ae:
        _db().crm_tasks.update_many({"lead_id": lead_id, "status": "open", "key": "handoff"},
                                    {"$set": {"owner_id": ae["_id"], "owner_name": ae["name"], "owner_role": "AE"}})
    if lead.get("status") == "done":
        ensure_tasks(db.leads().find_one({"_id": lead_id}), _member_ref(owner), _member_ref(ae), actor)
    return {"lead_id": lead_id, "owner": _member_ref(owner), "ae": _member_ref(ae), "rule": rule, "reason": text,
            "steps": decision["steps"] if not manual else [text]}


def auto_assign_all(actor="auto"):
    """Assign every finished, unassigned lead. Safe to run from two processes (guarded update)."""
    if not routing_config().get("auto_assign", True):
        return []
    done = []
    q = {"status": "done", "archived": {"$ne": True}, "crm.assignment": {"$exists": False}}
    for d in db.leads().find(q, {"_id": 1}).sort("created_at", 1).limit(50):
        try:
            r = assign(d["_id"], actor=actor, only_if_unassigned=True)
            if r:
                done.append(r)
        except Exception as e:  # one bad lead must not stop the rest
            log.warning("auto-assign %s failed: %s", d["_id"], e)
    # leads assigned before their stage outputs existed get their tasks once they are done
    for d in db.leads().find({"status": "done", "archived": {"$ne": True}, "crm.assignment": {"$exists": True},
                              "crm.tasks_made": {"$ne": True}}).limit(50):
        c = d.get("crm") or {}
        by_id = {m["_id"]: m for m in team()}
        ensure_tasks(d, _member_ref(by_id.get(c.get("owner_id"))), _member_ref(by_id.get(c.get("ae_id"))), actor)
        db.leads().update_one({"_id": d["_id"]}, {"$set": {"crm.tasks_made": True}})
    return done


class AutoAssigner:
    """Background thread in the web server: auto-assign every `interval` seconds."""

    def __init__(self, interval=20):
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None
        self.last_run = None
        self.last_error = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="crm-auto-assign", daemon=True)
        self._thread.start()

    def run_once(self):
        try:
            out = auto_assign_all()
            self.last_error = None
            return out
        except Exception as e:  # keep the loop alive (e.g. MongoDB briefly unreachable)
            self.last_error = str(e)[:200]
            log.warning("auto-assign tick failed: %s", e)
            return []
        finally:
            self.last_run = now()

    def _loop(self):
        while not self._stop.is_set():
            self.run_once()
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()


# ---------------------------------------------------------------- deals (one per lead)

def stage_of(status):
    s = status or "new"
    s = LEGACY_STAGE.get(s, s)
    return s if s in STAGES else "new"


def set_stage(lead_id, stage, actor="web", why=""):
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    lead = db.leads().find_one({"_id": lead_id}, {"crm": 1})
    if not lead:
        raise KeyError(lead_id)
    old = stage_of((lead.get("crm") or {}).get("status"))
    t = now()
    sets = {"crm.status": stage, "crm.stage_changed_at": t, "crm.updated_at": t}
    if stage != "new" and old == "new" and not (lead.get("crm") or {}).get("first_response_at") and stage != "lost":
        sets["crm.first_response_at"] = t
    db.leads().update_one({"_id": lead_id}, {"$set": sets})
    if old != stage:
        log_activity(lead_id, "stage", f"Deal moved {STAGE_LABEL[old]} -> {STAGE_LABEL[stage]}" + (f" ({why})" if why else ""), actor,
                     {"from": old, "to": stage})
    c = (lead.get("crm") or {})
    if stage == "handed_to_ae" and not c.get("ae_id"):
        # handoff without an AE: route the AE with the same rules
        members = team()
        cfg = routing_config()
        summary = (db.leads().find_one({"_id": lead_id}, {"summary": 1}) or {}).get("summary") or {}
        r = route({**summary, "tier": (cfg.get("ae_tiers") or ["P1"])[0]}, members, loads(exclude_lead=lead_id), cfg)
        if r["ae"]:
            assign(lead_id, actor=actor, ae_id=r["ae"]["id"], reason=f"AE added at handoff by the AE rules: {r['steps'][-2]}")
    return {"lead_id": lead_id, "from": old, "to": stage}


def _domain(email):
    m = re.search(r"@([\w.-]+\.\w+)", email or "")
    return m.group(1).lower() if m else None


def account_key(summary, gmail=None):
    s = summary or {}
    dom = _domain(s.get("email")) or _domain((gmail or {}).get("sender"))
    if dom and not FREE_MAIL.match(dom):
        return dom
    name = s.get("company") or s.get("company_full")
    return f"company:{_slug(name)}" if name else None


DEAL_PROJ = {"summary": 1, "crm": 1, "status": 1, "created_at": 1, "gmail": 1, "source": 1, "pdf_checklist_score": 1}


def deal_of(d):
    s, c = d.get("summary") or {}, d.get("crm") or {}
    return {"lead_id": d["_id"], "stage": stage_of(c.get("status")), "run_status": d.get("status"),
            "name": s.get("name"), "title": s.get("title"), "company": s.get("company"), "tier": s.get("tier"),
            "priority": s.get("priority"), "region": s.get("region"), "industry": s.get("industry"), "motion": s.get("motion"),
            "owner": c.get("owner"), "owner_id": c.get("owner_id"), "ae": c.get("ae"), "ae_id": c.get("ae_id"),
            "sla": sla_state(c), "created_at": d.get("created_at"), "stage_changed_at": c.get("stage_changed_at"),
            "account": account_key(s, d.get("gmail"))}


def pipeline():
    deals = [deal_of(d) for d in db.leads().find({"archived": {"$ne": True}}, DEAL_PROJ).sort("created_at", -1)]
    return {"stages": [{"key": k, "label": STAGE_LABEL[k], "count": sum(1 for x in deals if x["stage"] == k)} for k in STAGES],
            "deals": deals}


def accounts():
    groups = {}
    for d in db.leads().find({"archived": {"$ne": True}}, DEAL_PROJ).sort("created_at", -1):
        deal = deal_of(d)
        key = deal["account"] or f"lead:{d['_id']}"
        s = d.get("summary") or {}
        g = groups.setdefault(key, {"key": key, "company": None, "company_full": None, "domain": None, "country": None,
                                    "region": None, "industry": None, "contacts": {}, "leads": [], "owner": None, "ae": None})
        for k in ("company", "company_full", "country", "region", "industry"):
            g[k] = g[k] or s.get(k)
        if not key.startswith(("company:", "lead:")):
            g["domain"] = key
        g["owner"] = g["owner"] or deal["owner"]
        g["ae"] = g["ae"] or deal["ae"]
        ck = (s.get("email") or s.get("name") or d["_id"]).lower()
        g["contacts"].setdefault(ck, {"name": s.get("name"), "email": s.get("email"), "title": s.get("title"),
                                      "seniority": s.get("seniority"), "leads": 0})
        g["contacts"][ck]["leads"] += 1
        g["leads"].append(deal)
    out = []
    for g in groups.values():
        g["contacts"] = list(g["contacts"].values())
        stages = [x["stage"] for x in g["leads"]]
        g["open_deals"] = sum(1 for x in stages if x in OPEN_STAGES)
        g["best_tier"] = min([x["tier"] for x in g["leads"] if x["tier"]] or [None], key=lambda v: v or "P9")
        g["last_activity"] = max(x["created_at"] for x in g["leads"])
        out.append(g)
    out.sort(key=lambda g: g["last_activity"], reverse=True)
    return out


def account(key):
    return next((a for a in accounts() if a["key"] == key), None)


# ---------------------------------------------------------------- audit trail

def log_activity(lead_id, kind, text, actor="system", data=None):
    _db().crm_activity.insert_one({"lead_id": lead_id, "kind": kind, "text": str(text)[:1500], "actor": actor or "system",
                                   "data": data or {}, "at": now()})


def activity(lead_id=None, limit=200):
    q = {"lead_id": lead_id} if lead_id else {}
    out = list(_db().crm_activity.find(q).sort("at", DESCENDING).limit(limit))
    for x in out:
        x["_id"] = str(x["_id"])
    return out


# ---------------------------------------------------------------- dashboard

def dashboard():
    p = pipeline()
    deals = p["deals"]
    members = team()
    load = loads()
    open_tasks = list(_db().crm_tasks.find({"status": "open"}, {"owner_id": 1, "due_at": 1}))
    t = now()
    per = []
    for m in members:
        mine = [x for x in open_tasks if x.get("owner_id") == m["_id"]]
        cap = max(1, int(m.get("capacity") or 1))
        per.append({"id": m["_id"], "name": m["name"], "role": m["role"], "region": m.get("region"), "active": m.get("active", True),
                    "demo": m.get("demo", False), "open_leads": load.get(m["_id"], 0), "capacity": cap,
                    "utilisation": round(load.get(m["_id"], 0) / cap, 3), "open_tasks": len(mine),
                    "overdue_tasks": sum(1 for x in mine if _aware(x.get("due_at")) and _aware(x["due_at"]) < t)})
    breaches = [x for x in deals if x["sla"].get("state") == "breached"]
    at_risk = [x for x in deals if x["sla"].get("state") == "open" and x["sla"].get("seconds_left", 1e9) < 3600]
    unassigned = [x for x in deals if not x["owner_id"] and x["run_status"] == "done"]
    return {"pipeline": p["stages"], "deals_total": len(deals), "open_deals": sum(1 for x in deals if x["stage"] in OPEN_STAGES),
            "sla_breaches": breaches, "sla_at_risk": at_risk, "unassigned": unassigned, "load": per,
            "tasks_open": len(open_tasks),
            "tasks_overdue": sum(1 for x in open_tasks if _aware(x.get("due_at")) and _aware(x["due_at"]) < t),
            "sla_met": sum(1 for x in deals if x["sla"].get("state") == "met")}


def lead_view(lead_id):
    d = db.leads().find_one({"_id": lead_id}, DEAL_PROJ)
    if not d:
        return None
    c = d.get("crm") or {}
    return {"deal": deal_of(d), "assignment": c.get("assignment"), "sla": sla_state(c), "tasks": tasks(status="all", lead_id=lead_id),
            "activity": activity(lead_id), "stages": [{"key": k, "label": STAGE_LABEL[k]} for k in STAGES]}
