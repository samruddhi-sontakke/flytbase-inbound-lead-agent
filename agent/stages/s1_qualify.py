"""Stage 1: Qualification with MEDDPICC.

Design choice: the LLM only does the *reading* (what is known, what is missing,
rating each fit factor 0-5 with evidence). The *scoring* is plain Python below,
so the priority score is transparent, repeatable and easy to change.
"""
from .. import llm, log

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

PROMPT = """You are a senior enterprise BDR qualifying an inbound lead with MEDDPICC.
Use ONLY the structured lead below. Do not invent facts.

LEAD:
{lead}

Return JSON:
{{
  "elements": [
    {{"key": "M", "name": "Metrics", "status": "known|partial|unknown",
      "evidence": "exact detail from the lead, or null",
      "missing": "what we still need to learn",
      "discovery_question": "one natural question a BDR would ask to fill the gap"}}
    ... one object for EACH of: {elements}
  ],
  "fit_ratings": {{ "<factor>": {{"rating": 0-5, "reason": "short, evidence-based"}} ... for each of: {factors} }},
  "risks": ["things that could slow or kill the deal"],
  "summary": "2-3 sentence qualification verdict"
}}"""


def _score(result):
    fit = 0.0
    for factor, (weight, _) in FIT_FACTORS.items():
        r = result.get("fit_ratings", {}).get(factor, {}).get("rating", 0) or 0
        fit += weight * max(0, min(5, float(r))) / 5
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
    }


def run(lead):
    log.stage(1, f"Qualification - {FRAMEWORK}")
    import json
    prompt = PROMPT.format(
        lead=json.dumps(lead, indent=2, ensure_ascii=False),
        elements=", ".join(f"{k} {n}" for k, n, _ in ELEMENTS),
        factors=", ".join(f"{k} ({d})" for k, (_, d) in FIT_FACTORS.items()),
    )
    result = llm.ask(prompt, temperature=0.1, label="s1_qualify")
    result["framework"] = FRAMEWORK
    result["framework_rationale"] = FRAMEWORK_WHY
    result["fit_weights"] = {k: w for k, (w, _) in FIT_FACTORS.items()}
    result["scores"] = _score(result)
    known = [e["name"] for e in result.get("elements", []) if e.get("status") == "known"]
    unknown = [e["name"] for e in result.get("elements", []) if e.get("status") != "known"]
    s = result["scores"]
    log.ok(f"ICP fit {s['icp_fit_score']}/100 | MEDDPICC completeness {s['meddpicc_completeness']}% | {s['priority_tier']}")
    log.ok(f"Known: {', '.join(known) or 'none'}")
    log.ok(f"Gaps to discover: {', '.join(unknown)}")
    return result
