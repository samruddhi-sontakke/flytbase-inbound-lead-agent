"""Stage 2: Deep account research.

Three steps, each inspectable:
  1. PLAN    - the LLM writes search queries from the parsed lead (no hard-coded company).
  2. GATHER  - Tavily runs every query; each result is stored with a source ID.
  3. WRITE + VERIFY - the LLM writes the brief citing source IDs only, then a second,
               separate check confirms every claim is supported by the cited text.
               Unsupported claims are removed and listed in the output.
"""
import datetime
import json
import re

from .. import config, llm, log, tools

CATEGORIES = {
    "org_structure": "organisational structure, divisions, executives and reporting lines relevant to the contact",
    "budget_signals": "capex / opex guidance, investment plans, technology or automation spend from annual reports, 20-F or results",
    "recent_news": "news, press releases and strategic announcements from the last 12-18 months",
    "investor_priorities": "shareholder / investor letters, earnings calls, sustainability reports that reveal operational priorities",
    "operations_context": "the specific sites, operations, safety and workforce context mentioned in the lead",
    "technology_adoption": "drones, automation, digital innovation or remote operations already used by the company",
}

PLAN_PROMPT = """Today is {today}. Plan web research on this inbound lead's company.

LEAD:
{lead}

Write {n} precise web search queries covering these categories:
{cats}

Tips: use the company's full and short name; include document types (annual report, 20-F,
capex, investor presentation, sustainability report); include the current and previous year
where useful; include the contact's division and sites. Return JSON:
{{"queries": [{{"category": "<category key>", "query": "<search text>"}}]}}"""

WRITE_SYSTEM = (
    "You are a meticulous B2B account researcher. Every factual claim MUST cite one or more "
    "source IDs like [S3] that appear in the provided sources. If the sources do not contain "
    "something, say it was not found. Never use outside knowledge for facts, numbers, names or dates. "
    "Never name a person unless that name appears in the sources - not even in an inference. "
    "When sources conflict, use the MOST RECENT one and say which period it covers."
)

WRITE_PROMPT = """Today is {today}. Write a research brief on {company} for an inbound lead from {contact}, {title}.
Seller: {vendor} (autonomous drone / drone-in-a-box operations platform for large industrial sites).

LEAD CONTEXT:
{lead}

SOURCES:
{sources}

Return JSON:
{{
  "company_snapshot": [finding],
  "org_structure": {{
      "findings": [finding],
      "relevant_stakeholders": [{{"name": str, "title": str, "why_relevant": str, "source_ids": [str]}}],
      "likely_reporting_line": "how the contact's role probably fits, labelled as inference; use roles, not names, unless the name is in the sources"
  }},
  "budget_signals": [finding],
  "recent_news": [finding],
  "investor_priorities": [finding],
  "operations_context": [finding],
  "technology_adoption": [finding],
  "positioning_recommendation": {{
      "summary": "how {vendor} should position itself, 3-4 sentences",
      "angles": ["specific angle tied to a finding, with [S#]"],
      "risks_or_objections": [str]
  }},
  "not_found": ["important things we searched for but could not find"]
}}
where finding = {{"claim": "one factual sentence", "source_ids": ["S1"], "so_what": "why this matters for the deal"}}.
Prefer recent, specific, numeric facts over generic descriptions. 3-6 findings per list."""

VERIFY_PROMPT = """You are a fact-checker. For each claim, decide whether the cited source text supports it.
"supported" = clearly stated; "partial" = mostly supported but a detail (number/date/name) is not in the text;
"unsupported" = not in the text.

{items}

Return JSON: {{"results": [{{"n": int, "verdict": "supported|partial|unsupported", "note": str}}]}}"""

FINDING_LISTS = ["company_snapshot", "budget_signals", "recent_news", "investor_priorities",
                 "operations_context", "technology_adoption"]


def _collect_findings(brief):
    """Yield (path, finding) for every cited claim in the brief."""
    for key in FINDING_LISTS:
        for f in brief.get(key, []) or []:
            yield key, f
    for f in brief.get("org_structure", {}).get("findings", []) or []:
        yield "org_structure", f
    for p in brief.get("org_structure", {}).get("relevant_stakeholders", []) or []:
        yield "stakeholders", {"claim": f"{p.get('name')} is {p.get('title')}", "source_ids": p.get("source_ids", []), "_ref": p}


def _verify(brief, sources):
    items, refs = [], []
    all_findings = list(_collect_findings(brief))
    for path, f in all_findings:
        ids = [i for i in f.get("source_ids", []) if sources.get(i)]
        if not ids:
            f["verification"] = "unsupported"
            f["verification_note"] = "no valid source cited"
            continue
        excerpt = "\n".join(f"[{i}] {sources.get(i)['content'][:2500]}" for i in ids[:3])
        refs.append(f)
        items.append(f"CLAIM {len(refs)}: {f['claim']}\nCITED TEXT:\n{excerpt}\n")
    # verify in batches to stay well inside free-tier limits
    for start in range(0, len(items), 15):
        batch = items[start:start + 15]
        res = llm.ask(VERIFY_PROMPT.format(items="\n".join(batch)), temperature=0.0, label="s2_verify")
        for r in res.get("results", []):
            idx = start + int(r.get("n", 0)) - 1
            if 0 <= idx < len(refs):
                refs[idx]["verification"] = r.get("verdict", "unsupported")
                refs[idx]["verification_note"] = r.get("note", "")
    # remove unsupported claims, keep a record of what was removed
    removed = []
    for key in FINDING_LISTS:
        keep = []
        for f in brief.get(key, []) or []:
            (removed.append(f) if f.get("verification") == "unsupported" else keep.append(f))
        brief[key] = keep
    org = brief.get("org_structure", {})
    for key in ("findings",):
        keep = []
        for f in org.get(key, []) or []:
            (removed.append(f) if f.get("verification") == "unsupported" else keep.append(f))
        org[key] = keep
    # stakeholder names: copy the verdict back onto the person and drop unsupported ones
    keep_people = []
    for path, f in all_findings:
        if path != "stakeholders":
            continue
        person = f["_ref"]
        person["verification"] = f.get("verification", "unsupported")
        if person["verification"] == "unsupported":
            removed.append({"claim": f["claim"], "source_ids": f.get("source_ids"), "verification": "unsupported"})
        else:
            keep_people.append(person)
    org["relevant_stakeholders"] = keep_people
    brief["removed_by_fact_check"] = removed
    return brief


def run(lead, sources):
    log.stage(2, "Deep account research")
    company = lead["company"]["name"]
    today = datetime.date.today().isoformat()

    plan = llm.ask(
        PLAN_PROMPT.format(
            today=today, lead=json.dumps(lead, ensure_ascii=False), n=config.MAX_RESEARCH_QUERIES,
            cats="\n".join(f"- {k}: {v}" for k, v in CATEGORIES.items()),
        ),
        temperature=0.2, label="s2_plan",
    )
    queries = plan.get("queries", [])[: config.MAX_RESEARCH_QUERIES]
    log.ok(f"Planned {len(queries)} searches")

    # relevance filter: keep only results that actually mention the company
    names = {n.lower() for n in (lead["company"].get("short_name"), lead["company"].get("name")) if n}
    names |= {re.sub(r"\(.*?\)", "", n).strip() for n in names}
    dropped = 0
    for q in queries:
        log.step(f"[{q.get('category')}] {q.get('query')}")
        topic = "news" if q.get("category") == "recent_news" else "general"
        for r in tools.search(q["query"], max_results=config.RESEARCH_RESULTS_PER_QUERY, topic=topic):
            blob = f"{r['title']} {r['url']} {r['content']}".lower()
            if not any(n and n in blob for n in names):
                dropped += 1
                continue
            sources.add(r["url"], r["title"], r["content"], kind=q.get("category"), query=q["query"], published=r["published"])
    research_ids = list(sources.items.keys())
    log.ok(f"Collected {len(research_ids)} relevant sources ({dropped} off-topic results filtered out)")

    c = lead["contact"]
    brief = llm.ask(
        WRITE_PROMPT.format(
            today=today, company=company, contact=c.get("name"), title=c.get("title"), vendor="FlytBase",
            lead=json.dumps(lead, ensure_ascii=False), sources=sources.as_prompt(research_ids),
        ),
        system=WRITE_SYSTEM, temperature=0.2, label="s2_write",
    )
    log.step("Fact-checking every claim against its cited source")
    brief = _verify(brief, sources)
    kept = sum(1 for _ in _collect_findings(brief))
    log.ok(f"{kept} claims kept, {len(brief['removed_by_fact_check'])} removed by fact-check")
    brief["queries_run"] = queries
    return brief
