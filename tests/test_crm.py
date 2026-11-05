"""CRM: routing (territory, round-robin by load, P1 gets an AE, fallback), SLA, tasks from the stage outputs.
The pure functions need nothing; the flow test uses a throwaway MongoDB database (skipped without MongoDB)."""
import datetime

import pytest

from app import crm, db

UTC = datetime.timezone.utc
T0 = datetime.datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
TEAM = [{**m, "active": True, "last_assigned_at": None} for m in crm.DEMO_TEAM]
CFG = {**crm.DEFAULT_ROUTING}
SQM = {"region": "LATAM", "tier": "P1", "industry": "Mining", "sub_industry": "Lithium extraction", "company": "SQM"}


# ---------------------------------------------------------------- routing (pure)

def test_territory_picks_the_region_pool():
    r = crm.route({**SQM, "tier": "P3"}, TEAM, {}, CFG)
    assert r["rule"] == "territory:LATAM"
    assert r["owner"]["id"] in ("bdr-latam", "bdr-latam-2")
    assert r["ae"] is None and "No AE yet" in r["reason"]
    assert crm.route({"region": "EMEA", "tier": "P2"}, TEAM, {}, CFG)["owner"]["id"] == "bdr-emea"


def test_round_robin_by_load_and_capacity():
    # bdr-latam 5/25 = 0.20, bdr-latam-2 2/20 = 0.10 -> latam-2
    r = crm.route(SQM, TEAM, {"bdr-latam": 5, "bdr-latam-2": 2}, CFG)
    assert r["owner"]["id"] == "bdr-latam-2"
    # equal ratio -> whoever was assigned longest ago (never assigned beats assigned)
    team = [dict(m) for m in TEAM]
    next(m for m in team if m["_id"] == "bdr-latam")["last_assigned_at"] = T0
    r = crm.route(SQM, team, {"bdr-latam": 0, "bdr-latam-2": 0}, CFG)
    assert r["owner"]["id"] == "bdr-latam-2"
    # at capacity is skipped while someone has room, even if their ratio is lower otherwise
    r = crm.route(SQM, TEAM, {"bdr-latam": 3, "bdr-latam-2": 20}, CFG)
    assert r["owner"]["id"] == "bdr-latam"
    assert any(c["at_capacity"] for c in r["owner_candidates"])


def test_p1_gets_segment_ae_at_once():
    r = crm.route(SQM, TEAM, {}, CFG)
    assert r["ae"]["id"] == "ae-mining"
    assert "segment:Mining" in r["rule"]
    # no segment match -> AE fallback pool
    r = crm.route({"region": "EMEA", "tier": "P1", "industry": "Public Safety"}, TEAM, {}, CFG)
    assert r["ae"]["id"] == "ae-enterprise" and "ae_fallback" in r["rule"]
    # tiers that get an AE are configurable
    r = crm.route({**SQM, "tier": "P2"}, TEAM, {}, {**CFG, "ae_tiers": ["P1", "P2"]})
    assert r["ae"]["id"] == "ae-mining"


def test_fallback_pool_when_no_region_or_no_active_bdr():
    r = crm.route({"tier": "P2"}, TEAM, {}, CFG)
    assert r["rule"] == "fallback_pool" and r["owner"]["id"] in CFG["fallback_pool"]
    team = [{**m, "active": m["_id"] != "bdr-apac"} for m in TEAM]
    r = crm.route({"region": "APAC", "tier": "P3"}, team, {}, CFG)
    assert r["rule"] == "fallback_pool" and "no active BDR in the APAC territory" in r["reason"]


# ---------------------------------------------------------------- SLA

def test_sla_hours_and_state():
    assert crm.sla_hours("P1", CFG) == 1 and crm.sla_hours("P2", CFG) == 24 and crm.sla_hours("P3", CFG) == 72
    assert crm.sla_hours(None, CFG) == 24
    sla = {"tier": "P1", "hours": 1, "start": T0, "due_at": T0 + datetime.timedelta(hours=1)}
    assert crm.sla_state({"sla": sla}, at=T0 + datetime.timedelta(minutes=30))["state"] == "open"
    st = crm.sla_state({"sla": sla}, at=T0 + datetime.timedelta(hours=2))
    assert st["state"] == "breached" and st["overdue"]
    assert crm.sla_state({"sla": sla, "first_response_at": T0 + datetime.timedelta(minutes=40)})["state"] == "met"
    assert crm.sla_state({"sla": sla, "first_response_at": T0 + datetime.timedelta(hours=3)})["state"] == "breached"
    assert crm.sla_state({})["state"] == "none"


# ---------------------------------------------------------------- tasks

def test_parse_offset():
    assert crm.parse_offset("Within 1 hour")[:2] == (3600, False)
    assert crm.parse_offset("3 days after No-Reply")[:2] == (3 * 86400, True)
    assert crm.parse_offset("Day 7")[:2] == (7 * 86400, False)
    assert crm.parse_offset("Same business day")[0] == 8 * 3600
    assert crm.parse_offset("within 1 hour of inbound")[1] is False
    assert crm.parse_offset("whenever", default_hours=5)[0] == 5 * 3600


def test_plan_tasks_from_emails_and_handoff():
    lead = {"_id": "x", "result": {
        "emails": {"emails": [{"step": 1, "send_when": "Within 1 hour", "subject": "A"},
                              {"step": 2, "send_when": "3 days after No-Reply", "subject": "B"},
                              {"step": 3, "send_when": "5 days after No-Reply", "subject": "C"}]},
        "handoff": {"suggested_next_step": {"action": "Discovery call", "owner": "AE", "by_when": "Same business day"}}}}
    owner, ae = {"id": "bdr-latam", "name": "BDR"}, {"id": "ae-mining", "name": "AE"}
    t = {x["key"]: x for x in crm.plan_tasks(lead, owner, ae, T0)}
    assert set(t) == {"email-1", "email-2", "email-3", "handoff"}
    assert t["email-1"]["due_at"] == T0 + datetime.timedelta(hours=1)
    assert t["email-2"]["due_at"] == T0 + datetime.timedelta(hours=1, days=3)   # chained after email 1
    assert t["email-3"]["due_at"] == T0 + datetime.timedelta(hours=1, days=8)
    assert all(t[k]["owner_id"] == "bdr-latam" for k in ("email-1", "email-2", "email-3"))
    assert t["handoff"]["owner_id"] == "ae-mining" and t["handoff"]["due_at"] == T0 + datetime.timedelta(hours=8)
    # without an AE the BDR holds the handoff task
    t = {x["key"]: x for x in crm.plan_tasks(lead, owner, None, T0)}
    assert t["handoff"]["owner_id"] == "bdr-latam" and t["handoff"]["owner_role"] == "BDR"


def test_stage_mapping():
    assert crm.stage_of("handed_off") == "handed_to_ae" and crm.stage_of("working") == "contacted"
    assert crm.stage_of(None) == "new" and crm.stage_of("won") == "won" and crm.stage_of("junk") == "new"


def test_account_key():
    assert crm.account_key({"email": "r.castillo@sqm.cl", "company": "SQM"}) == "sqm.cl"
    assert crm.account_key({"email": "someone@gmail.com", "company": "Acme Mining"}) == "company:acme-mining"


# ---------------------------------------------------------------- flow on a throwaway database

@pytest.fixture()
def testdb():
    if not db.uri():
        pytest.skip("needs MongoDB")
    client = __import__("pymongo").MongoClient(db.uri(), serverSelectionTimeoutMS=8000, tz_aware=True)
    try:
        client.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB not reachable")
    old_db, old_client = db._db, db._client
    db._client = client
    db._db = client["leaddesk_pytest_crm"]
    client.drop_database("leaddesk_pytest_crm")
    crm.ensure()
    yield db._db
    client.drop_database("leaddesk_pytest_crm")
    db._db, db._client = old_db, old_client


def _lead(testdb, lid, summary, status="done", created=None):
    testdb.leads.insert_one({
        "_id": lid, "created_at": created or crm.now(), "status": status, "source": "web", "summary": summary,
        "crm": {"status": "new", "owner": "", "notes": []},
        "result": {"emails": {"emails": [{"step": 1, "send_when": "Within 1 hour", "subject": "Hi"},
                                         {"step": 2, "send_when": "3 days after no reply", "subject": "Follow"}]},
                   "handoff": {"suggested_next_step": {"action": "Discovery call", "by_when": "Same business day"}}}})


def test_auto_assign_flow(testdb):
    assert testdb.team.count_documents({"demo": True}) == len(crm.DEMO_TEAM)
    _lead(testdb, "l1", SQM)
    _lead(testdb, "l2", {**SQM, "tier": "P3", "name": "B"})
    _lead(testdb, "l3", {**SQM, "name": "C"}, status="running")  # not done: left alone
    out = crm.auto_assign_all()
    assert {o["lead_id"] for o in out} == {"l1", "l2"}
    assert crm.auto_assign_all() == []  # idempotent
    l1, l2 = testdb.leads.find_one({"_id": "l1"}), testdb.leads.find_one({"_id": "l2"})
    assert l1["crm"]["ae_id"] == "ae-mining" and l1["crm"]["sla"]["hours"] == 1
    assert {l1["crm"]["owner_id"], l2["crm"]["owner_id"]} == {"bdr-latam", "bdr-latam-2"}  # round-robin
    assert l2["crm"]["ae_id"] is None and l2["crm"]["sla"]["hours"] == 72
    assert "assignment" not in (testdb.leads.find_one({"_id": "l3"})["crm"])
    tasks = crm.tasks(lead_id="l1", status="all")
    assert {t["key"] for t in tasks} == {"email-1", "email-2", "handoff"}
    assert next(t for t in tasks if t["key"] == "handoff")["owner_id"] == "ae-mining"
    kinds = [a["kind"] for a in crm.activity("l1")]
    assert "assigned" in kinds and "tasks_created" in kinds

    # completing email 1 records the first response and moves the deal to contacted
    crm.complete_task("l1:email-1", actor="test")
    l1 = testdb.leads.find_one({"_id": "l1"})
    assert l1["crm"]["first_response_at"] and l1["crm"]["status"] == "contacted"
    assert crm.sla_state(l1["crm"])["state"] == "met"

    # manual reassign moves open email tasks and is audited
    r = crm.assign("l1", actor="test", owner_id="bdr-emea", reason="covering a holiday")
    assert r["rule"] == "manual"
    assert crm.tasks(lead_id="l1", status="open")[0]["owner_id"] in ("bdr-emea", "ae-mining")
    assert next(t for t in crm.tasks(lead_id="l1", status="all") if t["key"] == "email-2")["owner_id"] == "bdr-emea"
    assert crm.activity("l1")[0]["kind"] == "reassigned"
    with pytest.raises(ValueError):
        crm.assign("l1", owner_id="ae-mining", reason="wrong role")

    # handing a P3 deal to the AE adds an AE by the rules
    crm.set_stage("l2", "handed_to_ae", actor="test")
    assert testdb.leads.find_one({"_id": "l2"})["crm"]["ae_id"] == "ae-mining"

    d = crm.dashboard()
    assert d["deals_total"] == 3 and any(x["id"] == "ae-mining" and x["open_leads"] == 2 for x in d["load"])
    acc = crm.accounts()
    assert len(acc) == 1 and acc[0]["key"] == "company:sqm" and len(acc[0]["leads"]) == 3
