"""End-to-end through agent/store.py on a throwaway MongoDB database: inbox -> lead -> claim -> sources ->
every save_stage -> fact-check -> finish (report written). Stage outputs are replayed from a legacy run, so no AI
is involved. Skipped when no MongoDB connection string is configured."""
import json
import shutil

import pytest

from agent import config, store
from app import db

LEGACY = config.OUTPUT_DIR / "legacy_gemini" / "run_2026-11-05_16-34-35"
pytestmark = pytest.mark.skipif(not db.uri() or not LEGACY.exists(), reason="needs MongoDB and the legacy run folder")


@pytest.fixture()
def testdb():
    client = __import__("pymongo").MongoClient(db.uri(), serverSelectionTimeoutMS=8000, tz_aware=True)
    old = db._db
    db._db = None
    db._client = client
    test = client["leaddesk_pytest"]
    db._db = test
    for name, keys, kw in [("leads", "gmail.message_id", {"unique": True, "partialFilterExpression": {"gmail.message_id": {"$type": "string"}}})]:
        test[name].create_index(keys, **kw)
    test.sources.create_index([("lead_id", 1), ("id", 1)], unique=True)
    test.sources.create_index([("lead_id", 1), ("url", 1)], unique=True)
    yield test
    client.drop_database("leaddesk_pytest")
    db._db = old


def load(name):
    return json.loads((LEGACY / f"{name}.json").read_text(encoding="utf-8"))


def test_full_flow(testdb):
    body = (LEGACY / "input.txt").read_text(encoding="utf-8") if (LEGACY / "input.txt").exists() else \
        (config.ROOT / "input" / "lead_sqm.txt").read_text(encoding="utf-8")
    chk = store.inbox_check("m1", "t1", "forms@flytbase.com", "New contact", body)
    assert chk["hint"] == "likely_lead"
    v = store.inbox_verdict("m1", True, "contact form enquiry")
    assert store.inbox_verdict("m1", True, "again")["already_created"]  # dedupe
    claim = store.claim_next()
    assert claim["claimed"] == v["lead_id"]
    assert store.claim_next()["claimed"] is None  # one lead at a time
    lid = claim["claimed"]
    run_dir = config.ROOT / claim["run_dir"]
    try:
        # register the legacy sources under the same IDs (S1..Sn, in order)
        legacy_sources = json.loads((LEGACY / "sources.json").read_text(encoding="utf-8"))
        for s in legacy_sources:
            sid = store.add_source(lid, s["url"], s["title"], f"{s['title']} Adentu Dronestore", kind=s.get("kind") or "web")
            assert sid == s["id"]
        qual = load("1_qualification")
        data = {"lead": load("0_lead"), "elements": qual["elements"], "fit_ratings": qual["fit_ratings"],
                "risks": qual.get("risks"), "summary": qual.get("summary")}
        out = store.save_stage(lid, "qualification", data, agent="stage-1-qualify")
        assert out["scores"]["priority_score"] == qual["scores"]["priority_score"]

        research = load("2_research")
        research.pop("removed_by_fact_check", None)
        store.save_draft(lid, "research", research)
        claims = store.research_claims(lid)
        res = store.submit_fact_check(lid, [{"n": c["n"], "verdict": "supported"} for c in claims])
        assert res["fact_check"]["claims_checked"] == len(claims)

        case = load("4_case_study")
        store.save_work(lid, "case_study", {"scored": case.get("pre_scores"), "scanned": case.get("case_studies_scanned"),
                                            "urls": [p["url"] for p in case.get("pre_scores") or []], "inputs": {}})
        out = store.save_stage(lid, "case_study", {k: v for k, v in case.items() if k != "pre_scores"}, agent="stage-4-case-study")
        assert out["url_verified"]
        out = store.save_stage(lid, "partner", load("5_partner"), agent="stage-5-partner")
        assert out["motion"]
        em = load("3_emails")
        em["tone_adaptation"] = {"seniority": "s", "industry": "i", "stated_context": "c"}
        store.save_stage(lid, "emails", em, agent="stage-3-emails")
        store.save_stage(lid, "handoff", load("6_handoff"), agent="stage-6-handoff")
        done = store.finish(lid)
        assert done["status"] == "done"
        assert (run_dir / "REPORT.html").exists() and (run_dir / "trace.jsonl").exists()
        doc = testdb.leads.find_one({"_id": lid})
        assert doc["status"] == "done" and doc["summary"]["name"] and doc["pdf_checklist_score"]
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
