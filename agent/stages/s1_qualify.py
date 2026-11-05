"""Stage 1: Qualification (MEDDPICC). Deterministic part.

The `stage-1-qualify` subagent (.claude/agents/stage-1-qualify.md) does the reading: it extracts the known
information from the email, sets known / partial / unknown for each MEDDPICC element and rates each ICP fit
factor 0-5 with evidence. The scoring is plain Python here, so the priority score is transparent,
repeatable and easy to retune.
"""

FRAMEWORK = "MEDDPICC"
FRAMEWORK_WHY = (
    "MEDDPICC fits enterprise industrial deals like this one: a multi-site, multi-stakeholder "
    "purchase where safety, operations, IT/OT and procurement all have a say, and where a "
    "partner (integrator/reseller) often shapes the deal. BANT is too shallow for that buying "
    "committee, and SPICED is built for recurring SaaS expansion. MEDDPICC also makes the gaps "
    "explicit (Economic Buyer, Decision Process, Paper Process), which tells the BDR exactly "
    "what the first emails must uncover."
)

ELEMENTS = [
    ("M", "Metrics", "Quantified outcome the buyer wants (cost, hours, incidents, coverage)"),
    ("E", "Economic Buyer", "Person who owns the budget and can sign"),
    ("D1", "Decision Criteria", "Technical / commercial criteria used to choose a vendor"),
    ("D2", "Decision Process", "Steps, people and timeline to reach a decision"),
    ("P", "Paper Process", "Procurement, legal, security review, contracting path"),
    ("I", "Identify Pain", "Business pain and its consequence"),
    ("C1", "Champion", "Internal person who sells for us when we are not in the room"),
    ("C2", "Competition", "Alternatives: status quo, other vendors, build in-house"),
]

# Ideal Customer Profile factors and their weights (sum = 100). Edit here to retune.
FIT_FACTORS = {
    "industry_fit": (20, "Heavy industry with large outdoor assets (mining, energy, utilities, oil & gas, rail, ports)"),
    "site_scale": (15, "Number and size of sites"),
    "continuous_operations": (10, "24/7 or continuous operations that need recurring inspection"),
    "pain_severity": (15, "Cost, safety or hazard pain that autonomy directly removes"),
    "buyer_authority": (15, "Seniority and operational ownership of the contact"),
    "warm_introduction": (10, "Referral or existing relationship"),
    "timing_and_budget": (15, "Stated budget process or buying timeline"),
}

STATUS_POINTS = {"known": 1.0, "partial": 0.5, "unknown": 0.0}
LEAD_REQUIRED = ["contact", "company", "subject", "requested_solution", "use_cases", "sites", "pain_points",
                 "referral_source", "timeline_signals", "budget_signals", "search_keywords"]


def rubric():
    """What the subagent must fill in. Served by the MCP tool `get_rubric`, so Python stays the single source of truth."""
    return {
        "framework": FRAMEWORK, "framework_default_rationale": FRAMEWORK_WHY,
        "elements": [{"key": k, "name": n, "definition": d} for k, n, d in ELEMENTS],
        "fit_factors": [{"key": k, "weight": w, "definition": d} for k, (w, d) in FIT_FACTORS.items()],
        "statuses": list(STATUS_POINTS),
        "scoring": "priority = 0.7 x ICP fit + 0.3 x MEDDPICC completeness; tier set by ICP fit (>=75 P1, >=55 P2, else P3)",
    }


def score(result):
    fit, parts = 0.0, []
    for factor, (weight, _) in FIT_FACTORS.items():
        r = (result.get("fit_ratings", {}).get(factor) or {}).get("rating", 0) or 0
        r = max(0.0, min(5.0, float(r)))
        pts = weight * r / 5
        fit += pts
        parts.append(f"{factor} {r:g}/5 x {weight} = {pts:.1f}")
    elements = result.get("elements", [])
    completeness = 100 * sum(STATUS_POINTS.get(e.get("status", "unknown"), 0) for e in elements) / max(1, len(ELEMENTS))
    priority = round(0.7 * fit + 0.3 * completeness)
    if fit >= 75:
        tier = "P1 - Hot: respond same business day, involve AE early"
    elif fit >= 55:
        tier = "P2 - Warm: respond within 24h, BDR-led discovery"
    else:
        tier = "P3 - Nurture: automated nurture, re-qualify later"
    return {
        "icp_fit_score": round(fit),
        "meddpicc_completeness": round(completeness),
        "priority_score": priority,
        "priority_tier": tier,
        "formula": "priority = 0.7 x ICP fit + 0.3 x MEDDPICC completeness; tier set by ICP fit (>=75 P1, >=55 P2)",
        "calculation": parts + [f"ICP fit = {fit:.1f}", f"MEDDPICC completeness = {completeness:.1f}%",
                                f"priority = 0.7 x {fit:.1f} + 0.3 x {completeness:.1f} = {priority}"],
    }


def validate(data):
    """Return a list of problems; an empty list means the subagent output has the required shape."""
    problems = []
    lead = data.get("lead") or {}
    for k in LEAD_REQUIRED:
        if k not in lead:
            problems.append(f"lead.{k} missing")
    keys = {e.get("key") for e in data.get("elements") or []}
    for k, n, _ in ELEMENTS:
        if k not in keys:
            problems.append(f"MEDDPICC element {k} ({n}) missing")
    for e in data.get("elements") or []:
        if e.get("status") not in STATUS_POINTS:
            problems.append(f"element {e.get('key')} has status {e.get('status')!r}")
    for f in FIT_FACTORS:
        if f not in (data.get("fit_ratings") or {}):
            problems.append(f"fit_ratings.{f} missing")
    return problems


def postprocess(data):
    """Python adds the framework metadata and computes the scores. Returns (qualification, lead)."""
    lead = data.pop("lead")
    data["framework"] = FRAMEWORK
    data.setdefault("framework_rationale", FRAMEWORK_WHY)
    data["fit_weights"] = {k: w for k, (w, _) in FIT_FACTORS.items()}
    data["scores"] = score(data)
    data["known_information"] = [e["name"] for e in data.get("elements", []) if e.get("status") == "known"]
    data["missing_information"] = [{"element": e["name"], "status": e.get("status"), "missing": e.get("missing"),
                                    "discovery_question": e.get("discovery_question")}
                                   for e in data.get("elements", []) if e.get("status") != "known"]
    return data, lead


def checklist(q, lead):
    s = q.get("scores") or {}
    return [
        {"item": "Framework stated and explained", "ok": bool(q.get("framework") and q.get("framework_rationale"))},
        {"item": "Known information extracted from the email",
         "ok": bool(lead.get("contact", {}).get("name") and q.get("known_information")),
         "detail": ", ".join(q.get("known_information") or [])},
        {"item": "Missing information required for full qualification", "ok": bool(q.get("missing_information")),
         "detail": ", ".join(m["element"] for m in q.get("missing_information") or [])},
        {"item": "Fit assessment (every ICP factor rated with a reason)",
         "ok": all((q.get("fit_ratings", {}).get(f) or {}).get("reason") for f in FIT_FACTORS)},
        {"item": "Priority score with reasoning", "ok": bool(s.get("priority_score") is not None and q.get("summary")),
         "detail": f"{s.get('priority_score')}/100, {s.get('priority_tier')}"},
    ]
