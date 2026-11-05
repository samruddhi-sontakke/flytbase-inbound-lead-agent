"""Stage 6: AE handoff summary - everything an Account Executive needs on one page."""
import json

from .. import llm, log

PROMPT = """Write the AE handoff for this inbound lead. Be concise and actionable: an AE should read it in
2 minutes and know exactly what to do next. Use only the inputs below; keep [S#] citations on research facts.
Cite the exact source of each fact (facts about the vendor relationship cite the case study's source_id).
others_involved: use people named in the inputs (research stakeholders, case-study people_named); otherwise
describe a ROLE - never invent or infer a person's name.

LEAD: {lead}
QUALIFICATION: {qual}
RESEARCH: {research}
CASE STUDY: {case}
GTM / PARTNER: {partner}
EMAIL SEQUENCE PLAN: {emails}

Return JSON:
{{
  "one_line_summary": str,
  "buyer_context": {{"who": str, "what_he_cares_about": [str], "others_involved": [{{"name_or_role": str, "why": str}}]}},
  "qualification_status": {{"framework": str, "scores": str, "knowns": [str], "unknowns": [str]}},
  "top_3_research_highlights": [{{"finding": str, "source_ids": [str], "why_ae_should_care": str}}],
  "recommended_case_study": {{"title": str, "url": str, "why": str}},
  "gtm_motion": str,
  "suggested_next_step": {{"action": str, "owner": str, "by_when": str, "rationale": str}},
  "watch_outs": [str]
}}"""


def run(lead, qual, research, case, partner, emails):
    log.stage(6, "AE handoff summary")
    j = lambda x: json.dumps(x, ensure_ascii=False)
    result = llm.ask(
        PROMPT.format(
            lead=j(lead),
            qual=j({k: qual.get(k) for k in ("framework", "elements", "scores", "summary", "risks")}),
            research=j({k: v for k, v in research.items() if k not in ("removed_by_fact_check", "queries_run")}),
            case=j({k: case.get(k) for k in ("primary", "secondary", "referral_connection", "existing_relationship", "people_named")}),
            partner=j(partner),
            emails=j({"strategy": emails.get("sequence_strategy"), "subjects": [e.get("subject") for e in emails.get("emails", [])]}),
        ),
        temperature=0.2, label="s6_handoff",
    )
    log.ok(result.get("one_line_summary", ""))
    log.ok(f"Next step: {result.get('suggested_next_step', {}).get('action')}")
    return result
