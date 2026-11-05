"""Inbound Lead Desk - internal web app around the six-stage pipeline.

    py -m app.server            # http://127.0.0.1:8000  (local machine only)

* Each inbound email becomes one lead document in MongoDB.
* A single background worker runs the pipeline (agent/pipeline.py) one lead at a time,
  because the free-tier Gemini wrapper keeps per-process rate-limit state.
* Live progress comes from the same log messages the command line prints.
* Earlier command-line runs in outputs/ are imported on start-up, so nothing is lost.
"""
import contextlib
import datetime
import json
import os
import queue
import re
import threading
import traceback
from pathlib import Path

from bson import ObjectId
from fastapi import Body, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from agent import config, log, pipeline
from app import db

STATIC = Path(__file__).parent / "static"
STAGE_KEYS = {0: "lead", 1: "qualification", 2: "research", 3: "emails", 4: "case_study", 5: "partner", 6: "handoff"}
RUN_ORDER = ["lead", "qualification", "research", "case_study", "partner", "emails", "handoff"]
CRM_STATUSES = ["new", "working", "meeting_booked", "handed_off", "nurture", "disqualified"]

@contextlib.asynccontextmanager
async def lifespan(_app):
    startup()
    yield


app = FastAPI(title="FlytBase Inbound Lead Desk", docs_url="/api/docs", redoc_url=None, lifespan=lifespan)
jobs = queue.Queue()
state = {"current": None}


# ---------------------------------------------------------------- helpers

def summarize(result):
    """Flat fields for the lead list, taken from whatever stages have finished."""
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
    """Quick name/company for the list while intake is still running (no AI)."""
    out = {}
    m = re.search(r"From:\s*([^(<\n]+)", email_text)
    if m:
        out["name"] = m.group(1).strip()
    m = re.search(r"Company:\s*([^\n,]+)", email_text)
    if m:
        out["company"] = m.group(1).strip()
    m = re.search(r"Subject:\s*([^\n]+)", email_text)
    if m:
        out["subject"] = m.group(1).strip()
    return out


def public(doc, full=False):
    if not doc:
        return None
    doc = dict(doc)
    if not full:
        for k in ("result", "sources", "events", "email_text"):
            doc.pop(k, None)
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


# ---------------------------------------------------------------- worker

def process(lead_id):
    doc = db.leads().find_one({"_id": lead_id})
    if not doc:
        return
    run_dir = pipeline.new_run_dir()
    rel = run_dir.relative_to(config.ROOT).as_posix()
    db.leads().update_one({"_id": lead_id}, {"$set": {
        "status": "running", "run_dir": rel, "started_at": db.now(), "stage": None, "stages_done": [],
        "events": [], "error": None}})
    state["current"] = lead_id

    def on_log(kind, msg, seconds):
        upd = {"$push": {"events": {"t": seconds, "kind": kind, "msg": msg}}}
        if kind == "stage":
            num = int(msg.split("|", 1)[0])
            upd["$set"] = {"stage": STAGE_KEYS.get(num)}
        db.leads().update_one({"_id": lead_id}, upd)

    def on_stage_done(key, value):
        sets = {f"result.{key}": value}
        partial = (db.leads().find_one({"_id": lead_id}, {"result": 1}) or {}).get("result") or {}
        partial[key] = value
        sets["summary"] = {**doc.get("summary", {}), **{k: v for k, v in summarize(partial).items() if v}}
        db.leads().update_one({"_id": lead_id}, {"$set": sets, "$addToSet": {"stages_done": key}})

    log.listeners.append(on_log)
    try:
        result, sources = pipeline.run(doc["email_text"], run_dir, on_stage_done=on_stage_done)
        db.leads().update_one({"_id": lead_id}, {"$set": {
            "status": "done", "finished_at": db.now(), "result": result, "meta": result["meta"],
            "sources": sources.public_list(), "summary": summarize(result), "stage": None}})
    except Exception as e:
        traceback.print_exc()
        db.leads().update_one({"_id": lead_id}, {"$set": {
            "status": "failed", "finished_at": db.now(), "error": str(e)[:600]},
            "$push": {"events": {"t": None, "kind": "warn", "msg": f"Stopped: {str(e)[:300]}"}}})
    finally:
        log.listeners.remove(on_log)
        state["current"] = None


def worker():
    while True:
        lead_id = jobs.get()
        try:
            process(lead_id)
        except Exception:
            traceback.print_exc()


def import_old_runs():
    """Bring command-line runs from outputs/ into MongoDB (once each)."""
    count = 0
    for d in sorted(config.OUTPUT_DIR.glob("run_*")):
        if not (d / "6_handoff.json").exists() or db.leads().find_one({"_id": d.name}, {"_id": 1}):
            continue
        result = {}
        for key, name in pipeline.STAGE_FILES:
            f = d / f"{name}.json"
            result[key] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
        sources = json.loads((d / "sources.json").read_text(encoding="utf-8")) if (d / "sources.json").exists() else []
        calls = sum(1 for _ in open(d / "trace.jsonl", encoding="utf-8")) if (d / "trace.jsonl").exists() else None
        try:
            created = datetime.datetime.strptime(d.name, "run_%Y-%m-%d_%H-%M-%S").astimezone(datetime.timezone.utc)
        except ValueError:
            created = db.now()
        text_file = d / "input.txt" if (d / "input.txt").exists() else config.ROOT / "input" / "lead_sqm.txt"
        email_text = text_file.read_text(encoding="utf-8") if text_file.exists() else ""
        result["meta"] = {"started": created.astimezone().strftime("%Y-%m-%d %H:%M"), "llm_calls": calls,
                          "seconds": None, "input_file": "command line"}
        db.leads().insert_one({
            "_id": d.name, "created_at": created, "finished_at": created, "status": "done", "imported": True,
            "email_text": email_text, "run_dir": d.relative_to(config.ROOT).as_posix(), "result": result,
            "meta": result["meta"], "sources": sources, "summary": summarize(result),
            "stages_done": RUN_ORDER, "events": [], "crm": {"status": "new", "owner": "", "notes": []}})
        count += 1
    return count


def startup():
    db.get_db()
    db.leads().update_many({"status": "running"}, {"$set": {
        "status": "failed", "error": "Interrupted: the app was restarted while this lead was running."}})
    for d in db.leads().find({"status": "queued"}, {"_id": 1}).sort("created_at", 1):
        jobs.put(d["_id"])
    n = import_old_runs()
    if n:
        print(f"Imported {n} earlier run(s) from outputs/")
    threading.Thread(target=worker, daemon=True).start()


# ---------------------------------------------------------------- API

@app.get("/api/health")
def health():
    ok, info = db.ping()
    return {"mongo": ok, "database": info if ok else None, "mongo_error": None if ok else info,
            "missing_keys": config.check_keys(), "models": config.MODELS[:3],
            "running": state["current"], "queued": jobs.qsize()}


@app.get("/api/sample")
def sample():
    f = config.ROOT / "input" / "lead_sqm.txt"
    return {"email_text": f.read_text(encoding="utf-8") if f.exists() else ""}


@app.get("/api/leads")
def list_leads():
    docs = db.leads().find({}, {"result": 0, "sources": 0, "events": 0, "email_text": 0}).sort("created_at", -1)
    return [public(d) for d in docs]


@app.post("/api/leads")
def create_lead(body: dict = Body(...)):
    text = (body.get("email_text") or "").strip()
    if len(text) < 40:
        raise HTTPException(400, "Paste the full inbound email (at least a few lines).")
    if len(text) > 20000:
        raise HTTPException(400, "That email is too long (20,000 characters max).")
    missing = config.check_keys()
    if missing:
        raise HTTPException(400, f"Missing API key(s) in .env: {', '.join(missing)}")
    lead_id = str(ObjectId())
    db.leads().insert_one({
        "_id": lead_id, "created_at": db.now(), "status": "queued", "email_text": text,
        "summary": guess_contact(text), "stages_done": [], "events": [], "result": {},
        "crm": {"status": "new", "owner": "", "notes": []}})
    jobs.put(lead_id)
    return {"id": lead_id, "position": jobs.qsize()}


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
        sets["crm.status"] = body["status"]
    if "owner" in body:
        sets["crm.owner"] = str(body["owner"])[:80]
    if not sets:
        raise HTTPException(400, "Nothing to update")
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
    return create_lead({"email_text": doc.get("email_text") or ""})


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
    docs = db.leads().find({}, {"summary": 1, "created_at": 1, "finished_at": 1, "status": 1, "crm": 1, "meta": 1,
                                "imported": 1, "error": 1}).sort("created_at", -1).limit(100)
    for d in docs:
        s = d.get("summary") or {}
        who = f"{s.get('name') or 'Unknown'} · {s.get('company') or ''}".strip(" ·")
        items.append({"at": d["created_at"], "kind": "imported" if d.get("imported") else "received", "lead": d["_id"],
                      "title": who, "note": s.get("subject") or ""})
        if d.get("finished_at") and not d.get("imported"):
            if d["status"] == "done":
                m = d.get("meta") or {}
                items.append({"at": d["finished_at"], "kind": "qualified", "lead": d["_id"], "title": who,
                              "note": f"{s.get('tier') or ''} · priority {s.get('priority')} · {m.get('seconds')}s, "
                                      f"{m.get('llm_calls')} AI calls".strip(" ·")})
            elif d["status"] == "failed":
                items.append({"at": d["finished_at"], "kind": "failed", "lead": d["_id"], "title": who,
                              "note": d.get("error") or ""})
        for n in (d.get("crm") or {}).get("notes") or []:
            items.append({"at": n["at"], "kind": "note", "lead": d["_id"], "title": who, "note": n["text"]})
    items.sort(key=lambda i: i["at"], reverse=True)
    return jsonable_encoder(items[:150])


@app.exception_handler(RuntimeError)
def runtime_error(_, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("APP_HOST", "127.0.0.1")  # internal tool: local machine only by default
    port = int(os.environ.get("APP_PORT", "8000"))
    print(f"\nInbound Lead Desk running at http://{host}:{port}\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
