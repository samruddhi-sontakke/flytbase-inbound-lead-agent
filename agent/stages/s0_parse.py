"""Stage 0 (intake): turn the raw inbound email into structured fields.

Every later stage works from this structured lead, so nothing about SQM,
Chile, mining or Anglo American is hard-coded anywhere in the system.
"""
from .. import llm, log

SYSTEM = (
    "You are the intake step of an inbound sales pipeline. Extract ONLY what the email "
    "actually says. Never guess. Use null when something is not stated."
)

PROMPT = """Extract the lead below into JSON with exactly this shape:
{{
  "contact": {{"name": str, "email": str, "title": str, "division": str|null, "seniority": "C-level|VP|Head/Director|Manager|Individual contributor|unknown"}},
  "company": {{"name": str, "short_name": str, "country": str, "region": str, "email_domain": str, "industry": str, "sub_industry": str|null}},
  "subject": str,
  "requested_solution": str,
  "use_cases": [str],
  "sites": {{"count": int|null, "description": str|null, "location": str|null, "operating_hours": str|null}},
  "pain_points": [str],
  "referral_source": str|null,
  "timeline_signals": [str],
  "budget_signals": [str],
  "search_keywords": [str]   // 6-10 short terms describing industry, use case, environment, geography
}}
"region" must be a sales region such as LATAM, North America, EMEA, APAC.

INBOUND EMAIL:
---
{email}
---"""


def run(email_text):
    log.stage(0, "Intake - reading the inbound email")
    lead = llm.ask(PROMPT.format(email=email_text), system=SYSTEM, temperature=0.0, label="s0_parse")
    c, co = lead.get("contact", {}), lead.get("company", {})
    log.ok(f"Lead: {c.get('name')} | {c.get('title')} | {co.get('name')} ({co.get('country')})")
    log.ok(f"Referral source detected: {lead.get('referral_source')}")
    return lead
