"""Inbound Lead Desk - internal web app over the agent's MongoDB data.

    py -m app.server            # http://127.0.0.1:8000  (local machine only)

* The AI agent is Claude Code (see .claude/skills/process-inbox). On a session cron it reads unread Gmail,
  turns inbound leads into lead documents, runs the six stages with subagents and writes every result here
  through the leaddesk MCP server (agent/store.py).
* This app never calls an AI model and never sends email. Leads pasted here are only queued; the agent's next
  tick picks them up. Live progress is the `events` list the agent appends to.
"""
import contextlib
import datetime
import json
import os
import re
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from agent import config, store
from app import crm, db

STATIC = Path(__file__).parent / "static"
# Deal stages (app/crm.py). The first desk values (working, handed_off, disqualified) are still accepted and mapped.
CRM_STATUSES = crm.STAGES + list(crm.LEGACY_STAGE)
LIVE = {"archived": {"$ne": True}}
# Background auto-assign: every N seconds, finished and unassigned leads are routed (app/crm.py). CRM_AUTO_ASSIGN=0 turns it off.
# The demo CRM is off unless LEADDESK_CRM=1: no auto-assign thread, no CRM events in activity, hidden from /api/docs.
CRM_ON = os.environ.get("LEADDESK_CRM") == "1"
ASSIGNER = crm.AutoAssigner(interval=int(os.environ.get("CRM_AUTO_ASSIGN_SECONDS", "20")))


@contextlib.asynccontextmanager
async def lifespan(_app):
    startup()
    if os.environ.get("CRM_AUTO_ASSIGN", "1") != "0":
        if CRM_ON:
            ASSIGNER.start()
    yield
    ASSIGNER.stop()


app = FastAPI(title="FlytBase Inbound Lead Desk", docs_url="/api/docs", redoc_url=None, lifespan=lifespan)


# ---------------------------------------------------------------- helpers

def public(doc, full=False):
    if not doc:
        return None
    doc = dict(doc)
    doc.pop("work", None)
    doc.pop("drafts", None)
    if not full:
        for k in ("result", "sources", "events", "email_text"):
            doc.pop(k, None)
    c = dict(doc.get("crm") or {})
    if not full:
        c.pop("assignment", None)
        doc["crm"] = c
    doc["sla"] = crm.sla_state(c)
    doc["deal_stage"] = crm.stage_of(c.get("status"))
    return jsonable_encoder(doc)


def get_lead(lead_id):
    doc = db.leads().find_one({"_id": lead_id})
    if not doc:
        raise HTTPException(404, "Lead not found")
    return doc


def run_dir_of(doc):
    if not doc.get("run_dir"):
        raise HTTPException(404, "This lead has no run folder yet")
    return config.ROOT / doc["run_dir"]


def startup():
    db.get_db()
    # The Gemini-era runs (v0) are kept on disk in outputs/legacy_gemini/ but hidden from the desk.
    # Any lead without a `source` field predates the agent (v0); it stays in MongoDB but leaves the desk.
    db.leads().update_many({"source": {"$exists": False}, "archived": {"$ne": True}}, {"$set": {"archived": True}})
    crm.ensure()  # indexes, demo team and default routing rules (only when missing)


# ---------------------------------------------------------------- API

def _iso(v):
    return v.isoformat() if isinstance(v, datetime.datetime) else v


@app.get("/api/health")
def health():
    ok, info = db.ping()
    out = {"mongo": ok, "database": info if ok else None, "mongo_error": None if ok else info, "missing_keys": config.check_keys()}
    if ok:
        st = store.agent_state()
        q = store.queue_status()
        out.update({
            "agent": "Claude Code (session cron, /process-inbox)",
            "last_tick": _iso(st.get("last_tick")), "last_inbox_sweep": _iso(st.get("last_inbox_sweep")),
            "last_inbox_note": st.get("last_inbox_sweep_note"), "ticks": st.get("count_tick", 0),
            "running": next((x["lead_id"] for x in q if x["status"] == "running"), None),
            "queued": sum(1 for x in q if x["status"] == "queued"),
            "inbox_seen": db.get_db().inbox_log.count_documents({}),
        })
    return out


@app.get("/api/inbox")
def inbox():
    return jsonable_encoder(store.inbox_list())


@app.get("/api/sample")
def sample():
    f = config.ROOT / "input" / "lead_sqm.txt"
    return {"email_text": f.read_text(encoding="utf-8") if f.exists() else ""}


@app.get("/api/leads")
def list_leads():
    docs = db.leads().find(LIVE, {"result": 0, "sources": 0, "events": 0, "email_text": 0, "drafts": 0, "work": 0}).sort("created_at", -1)
    return [public(d) for d in docs]


@app.post("/api/leads")
def create_lead(body: dict = Body(...)):
    text = (body.get("email_text") or "").strip()
    if len(text) < 40:
        raise HTTPException(400, "Paste the full inbound email (at least a few lines).")
    if len(text) > 20000:
        raise HTTPException(400, "That email is too long (20,000 characters max).")
    lead_id = store.create_lead(text, source=body.get("source") or "web")
    position = db.leads().count_documents({"status": "queued"})
    return {"id": lead_id, "position": position}


@app.get("/api/leads/{lead_id}")
def lead_detail(lead_id: str):
    return public(get_lead(lead_id), full=True)


@app.get("/api/leads/{lead_id}/progress")
def lead_progress(lead_id: str, after: int = 0):
    doc = db.leads().find_one({"_id": lead_id}, {"status": 1, "stage": 1, "stages_done": 1, "events": 1, "error": 1,
                                                  "summary": 1})
    if not doc:
        raise HTTPException(404, "Lead not found")
    events = doc.get("events") or []
    return jsonable_encoder({"status": doc["status"], "stage": doc.get("stage"), "stages_done": doc.get("stages_done", []),
                             "error": doc.get("error"), "events": events[after:], "total": len(events),
                             "summary": doc.get("summary")})


@app.patch("/api/leads/{lead_id}")
def update_lead(lead_id: str, body: dict = Body(...)):
    get_lead(lead_id)
    sets = {}
    if "status" in body:
        if body["status"] not in CRM_STATUSES:
            raise HTTPException(400, "Unknown status")
    if "owner" in body:
        sets["crm.owner"] = str(body["owner"])[:80]
    if not sets and "status" not in body:
        raise HTTPException(400, "Nothing to update")
    if "status" in body:  # the deal stage: logged in the CRM audit trail
        crm.set_stage(lead_id, crm.stage_of(body["status"]), actor=str(body.get("actor") or "web")[:80])
    if sets:
        sets["crm.updated_at"] = db.now()
        db.leads().update_one({"_id": lead_id}, {"$set": sets})
    return public(get_lead(lead_id))


@app.post("/api/leads/{lead_id}/notes")
def add_note(lead_id: str, body: dict = Body(...)):
    get_lead(lead_id)
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "Write a note first")
    note = {"at": db.now(), "text": text[:4000], "author": (body.get("author") or "").strip()[:80]}
    db.leads().update_one({"_id": lead_id}, {"$push": {"crm.notes": note}})
    return jsonable_encoder(note)


@app.post("/api/leads/{lead_id}/rerun")
def rerun(lead_id: str):
    doc = get_lead(lead_id)
    return create_lead({"email_text": doc.get("email_text") or "", "source": doc.get("source") or "web"})


@app.get("/api/leads/{lead_id}/trace")
def trace(lead_id: str):
    f = run_dir_of(get_lead(lead_id)) / "trace.jsonl"
    if not f.exists():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


@app.get("/api/leads/{lead_id}/report")
def report_html(lead_id: str):
    f = run_dir_of(get_lead(lead_id)) / "REPORT.html"
    if not f.exists():
        raise HTTPException(404, "The report is written when the run finishes")
    return FileResponse(f, media_type="text/html")


@app.get("/api/leads/{lead_id}/report.md")
def report_md(lead_id: str):
    doc = get_lead(lead_id)
    f = run_dir_of(doc) / "REPORT.md"
    if not f.exists():
        raise HTTPException(404, "The report is written when the run finishes")
    name = re.sub(r"[^A-Za-z0-9]+", "_", (doc.get("summary") or {}).get("company") or "lead").strip("_")
    return FileResponse(f, media_type="text/markdown", filename=f"{name}_lead_report.md")


@app.get("/api/activity")
def activity():
    items = []
    docs = db.leads().find(LIVE, {"summary": 1, "source": 1, "created_at": 1, "finished_at": 1, "status": 1, "crm": 1, "meta": 1,
                                "imported": 1, "error": 1}).sort("created_at", -1).limit(100)
    for d in docs:
        s = d.get("summary") or {}
        who = f"{s.get('name') or 'Unknown'} · {s.get('company') or ''}".strip(" ·")
        items.append({"at": d["created_at"], "kind": "received", "lead": d["_id"],
                      "title": who, "note": f"via {d.get('source') or 'web'} · {s.get('subject') or ''}"})
        if d.get("finished_at"):
            if d["status"] == "done":
                m = d.get("meta") or {}
                items.append({"at": d["finished_at"], "kind": "qualified", "lead": d["_id"], "title": who,
                              "note": f"{s.get('tier') or ''} · priority {s.get('priority')} · {m.get('seconds')}s, "
                                      f"{m.get('llm_calls')} subagent calls".strip(" ·")})
            elif d["status"] == "failed":
                items.append({"at": d["finished_at"], "kind": "failed", "lead": d["_id"], "title": who,
                              "note": d.get("error") or ""})
        for n in (d.get("crm") or {}).get("notes") or []:
            items.append({"at": n["at"], "kind": "note", "lead": d["_id"], "title": who, "note": n["text"]})
    names = {d["_id"]: d.get("summary") or {} for d in db.leads().find(LIVE, {"summary": 1})}
    for a in (crm.activity(limit=150) if CRM_ON else []):
        if a.get("lead_id") and a["lead_id"] not in names:
            continue
        s = names.get(a.get("lead_id")) or {}
        title = f"{s.get('name') or 'Unknown'} · {s.get('company') or ''}".strip(" ·") if a.get("lead_id") else "CRM"
        items.append({"at": a["at"], "kind": "crm", "lead": a.get("lead_id"), "title": title,
                      "note": f"{a['kind'].replace('_', ' ')} · {a['text']}"})
    items.sort(key=lambda i: i["at"], reverse=True)
    return jsonable_encoder(items[:150])


# ---------------------------------------------------------------- CRM (app/crm.py): demo team, routing, tasks, deals

def _member(mid):
    m = db.get_db().team.find_one({"_id": mid})
    if not m:
        raise HTTPException(404, "No team member with that id")
    return m


def _actor(body):
    return str((body or {}).get("actor") or "web")[:80]


@app.get("/api/crm/team")
def crm_team():
    load = crm.loads()
    out = []
    for m in crm.team():
        cap = max(1, int(m.get("capacity") or 1))
        out.append({**m, "open_leads": load.get(m["_id"], 0), "utilisation": round(load.get(m["_id"], 0) / cap, 3)})
    return jsonable_encoder(out)


@app.post("/api/crm/team")
def crm_team_create(body: dict = Body(...)):
    fields, problems = crm.clean_member(body)
    if problems:
        raise HTTPException(400, "; ".join(problems))
    return jsonable_encoder(crm.create_member(fields, actor=_actor(body)))


@app.patch("/api/crm/team/{mid}")
def crm_team_update(mid: str, body: dict = Body(...)):
    _member(mid)
    fields, problems = crm.clean_member(body, partial=True)
    if problems:
        raise HTTPException(400, "; ".join(problems))
    if not fields:
        raise HTTPException(400, "Nothing to update")
    return jsonable_encoder(crm.update_member(mid, fields, actor=_actor(body)))


@app.get("/api/crm/routing")
def crm_routing():
    alive = ASSIGNER._thread is not None and ASSIGNER._thread.is_alive()
    return jsonable_encoder({**crm.routing_config(), "regions": crm.REGIONS, "stages": crm.STAGES,
                             "auto_assigner": {"running": alive, "interval_seconds": ASSIGNER.interval,
                                               "last_run": ASSIGNER.last_run, "last_error": ASSIGNER.last_error}})


@app.put("/api/crm/routing")
def crm_routing_put(body: dict = Body(...)):
    clean, problems = crm.validate_routing(body, {m["_id"] for m in crm.team()})
    if problems:
        raise HTTPException(400, "; ".join(problems))
    if not clean:
        raise HTTPException(400, "Nothing to update")
    return jsonable_encoder(crm.save_routing(clean, actor=_actor(body)))


@app.post("/api/crm/routing/explain")
def crm_explain(body: dict = Body(default={})):
    """How a lead (lead_id) or a hypothetical one (region, tier, industry) would be routed right now. Writes nothing."""
    if body.get("lead_id"):
        doc = get_lead(body["lead_id"])
        summary, exclude = doc.get("summary") or {}, doc["_id"]
    else:
        summary, exclude = {k: body.get(k) for k in ("region", "tier", "industry", "sub_industry")}, None
    return jsonable_encoder(crm.route(summary, crm.team(), crm.loads(exclude_lead=exclude), crm.routing_config()))


@app.post("/api/crm/auto-assign")
def crm_auto_assign():
    return jsonable_encoder({"assigned": ASSIGNER.run_once(), "last_error": ASSIGNER.last_error})


@app.get("/api/crm/leads/{lead_id}")
def crm_lead(lead_id: str):
    get_lead(lead_id)
    return jsonable_encoder(crm.lead_view(lead_id))


@app.post("/api/crm/leads/{lead_id}/assign")
def crm_assign(lead_id: str, body: dict = Body(default={})):
    """No owner_id/ae_id: run the routing rules again. With them: hand-pick (a reason is required)."""
    get_lead(lead_id)
    owner_id, ae_id = body.get("owner_id") or None, body.get("ae_id")
    reason = (body.get("reason") or "").strip()
    if (owner_id or ae_id is not None) and len(reason) < 3:
        raise HTTPException(400, "Say why you are reassigning (it goes in the audit trail).")
    try:
        r = crm.assign(lead_id, actor=_actor(body), owner_id=owner_id, ae_id=ae_id, reason=reason or None)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return jsonable_encoder(r)


@app.get("/api/crm/tasks")
def crm_tasks(owner: str = "", status: str = "open", lead_id: str = ""):
    return jsonable_encoder(crm.tasks(owner_id=owner or None, status=status, lead_id=lead_id or None))


@app.post("/api/crm/tasks")
def crm_task_add(body: dict = Body(...)):
    title = (body.get("title") or "").strip()
    get_lead(body.get("lead_id"))
    if not title:
        raise HTTPException(400, "A task needs a title")
    try:
        hours = float(body.get("due_in_hours") or 24)
    except (TypeError, ValueError):
        raise HTTPException(400, "due_in_hours must be a number")
    due = db.now() + datetime.timedelta(hours=hours)
    return jsonable_encoder(crm.add_task(body["lead_id"], title, body.get("owner_id"), due, actor=_actor(body)))


@app.post("/api/crm/tasks/{task_id}/complete")
def crm_task_done(task_id: str, body: dict = Body(default={})):
    t = crm.complete_task(task_id, actor=_actor(body), note=str(body.get("note") or ""))
    if not t:
        raise HTTPException(404, "No open task with that id")
    return jsonable_encoder(t)


@app.get("/api/crm/activity")
def crm_activity(lead_id: str = "", limit: int = 200):
    return jsonable_encoder(crm.activity(lead_id or None, limit=max(1, min(limit, 500))))


@app.get("/api/crm/pipeline")
def crm_pipeline():
    return jsonable_encoder(crm.pipeline())


@app.patch("/api/crm/deals/{lead_id}")
def crm_deal(lead_id: str, body: dict = Body(...)):
    get_lead(lead_id)
    try:
        r = crm.set_stage(lead_id, body.get("stage"), actor=_actor(body), why=str(body.get("why") or "")[:200])
    except ValueError as e:
        raise HTTPException(400, str(e))
    return jsonable_encoder(r)


@app.get("/api/crm/accounts")
def crm_accounts():
    return jsonable_encoder(crm.accounts())


@app.get("/api/crm/accounts/{key}")
def crm_account(key: str):
    a = crm.account(key)
    if not a:
        raise HTTPException(404, "No account with that key")
    return jsonable_encoder(a)


@app.get("/api/crm/dashboard")
def crm_dashboard():
    return jsonable_encoder(crm.dashboard())


@app.exception_handler(RuntimeError)
def runtime_error(_, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


if not CRM_ON:
    for _r in app.routes:
        if getattr(_r, "path", "").startswith("/api/crm"):
            _r.include_in_schema = False

app.mount("/static", StaticFiles(directory=STATIC), name="static")


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("APP_HOST", "127.0.0.1")  # internal tool: local machine only by default
    port = int(os.environ.get("APP_PORT", "8000"))
    print(f"\nInbound Lead Desk running at http://{host}:{port}\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
