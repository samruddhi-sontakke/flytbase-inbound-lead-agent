"""Stage 3: Adaptive response email sequence.

Runs AFTER research, case study and partner stages so the emails can use all of them.
Each email is mapped to the MEDDPICC gaps it is designed to uncover, and the
sequence branches depending on how the buyer replies.
"""
import json

from .. import config, llm, log

SYSTEM = (
    "You are a top-performing enterprise inbound BDR. You write short, specific, respectful emails "
    "to senior operations leaders in heavy industry. No hype, no buzzwords, no fake urgency. "
    "Every specific fact you mention about the buyer's company must come from the research provided."
)

PROMPT = """Write an adaptive email sequence replying to this inbound lead.

LEAD (the email they sent us):
{lead}

QUALIFICATION GAPS TO DISCOVER (MEDDPICC elements not yet known):
{gaps}

RESEARCH BRIEF (cited, fact-checked):
{research}

BEST CASE STUDY:
{case}

GO-TO-MARKET MOTION / PARTNER:
{partner}

Requirements:
- Email 1 MUST explicitly mention (a) the referral source by name and what the vendor did for them,
  and (b) if the case study shows his company already works with the vendor, that existing deployment
  (which operation, which partner, one result) - and ask how his sites relate to it. These are the
  strongest hooks; never replace them with vague phrases like "I am familiar with your work".
- Use the MOST RECENT figures from the research; never quote a figure from an older report if a newer one exists.
- Sign every email as: {bdr}, Business Development, {vendor}.
- Email 1 is the same-day reply to an inbound request: thank, show we understood their exact context,
  give one relevant proof point, ask at most 2 questions, propose a short call with 2 time options.
- Later emails each target different gaps, add new value (a proof point, a research insight, a resource),
  and get shorter. Adapt tone to a senior Head of Operations in mining in Chile: direct, safety-first,
  operational outcomes. Offer to continue in Spanish if helpful.
- If the research shows his company already works with the vendor or a partner, use that carefully
  (e.g. "your team at X already ..."), and never claim things the sources do not say.
- Include branches: what we send if he replies positively, if he says "not until Q3 / budget",
  or if he refers us to someone else.

Return JSON:
{{
  "sequence_strategy": "2-3 sentences on the overall logic",
  "emails": [
    {{"step": 1, "send_when": "e.g. within 1 hour of inbound", "goal": str,
      "meddpicc_gaps_targeted": [str], "research_used": ["S#"],
      "subject": str, "body": "full email text, signed as the FlytBase BDR",
      "why_this_email_now": str, "success_signal": str}}
  ],
  "branches": [{{"if_reply": str, "next_action": str, "draft_reply": str}}]
}}
Write 4 emails."""


def run(lead, qual, research, case, partner):
    log.stage(3, "Response generation - adaptive email sequence")
    gaps = [
        {"element": e.get("name"), "missing": e.get("missing"), "question": e.get("discovery_question")}
        for e in qual.get("elements", []) if e.get("status") != "known"
    ]
    research_short = {k: research.get(k) for k in (
        "company_snapshot", "org_structure", "budget_signals", "recent_news", "investor_priorities",
        "operations_context", "technology_adoption", "positioning_recommendation")}
    case_short = {k: case.get(k) for k in ("primary", "secondary", "referral_connection", "existing_relationship", "people_named")}
    partner_short = {k: partner.get(k) for k in ("motion", "recommended_partners", "roles")}
    result = llm.ask(
        PROMPT.format(
            lead=json.dumps(lead, ensure_ascii=False), gaps=json.dumps(gaps, ensure_ascii=False),
            research=json.dumps(research_short, ensure_ascii=False),
            case=json.dumps(case_short, ensure_ascii=False), partner=json.dumps(partner_short, ensure_ascii=False),
            bdr=config.BDR_NAME, vendor=config.VENDOR_NAME,
        ),
        system=SYSTEM, temperature=0.5, label="s3_emails",
    )
    for e in result.get("emails", []):
        log.ok(f"Email {e.get('step')} ({e.get('send_when')}): {e.get('subject')}  -> gaps: {', '.join(e.get('meddpicc_gaps_targeted', []))}")
    return result
