"""Stage 5: Partner identification and go-to-market motion.

1. DISCOVER - find the vendor's partner pages from its sitemap and read the partner directory.
2. SEARCH   - web search for vendor partners in the lead's country / region.
3. CONNECT  - pull in any partner named in case studies that involve the lead's own company.
4. DECIDE (LLM) - direct AE vs partner-led, using region, deal complexity and partner availability.
5. VERIFY (Python) - every partner name recommended must appear in a source text; otherwise flagged.
"""
import json

from .. import config, llm, log, tools

PROMPT = """Recommend the go-to-market motion for this inbound lead.

LEAD:
{lead}

QUALIFICATION SUMMARY:
{qual}

CASE STUDY FINDINGS (including any existing relationship between the lead's company and the vendor):
{case}

VENDOR PARTNER DIRECTORY AND PARTNER SEARCH RESULTS:
{partners}

Rules: only name partners that appear in the text above. If a partner ALREADY delivered a {vendor}
project for this same account (see the case study findings), recommend that partner FIRST: it already
knows the sites, the people and the procurement path. Other in-country directory partners are backups. Consider: region and language, on-the-ground
deployment and support needs (remote sites, hardware, docks), deal complexity (sites, stakeholders,
enterprise procurement), partner availability in the country/region, and any partner already working
with this account. Return JSON:
{{
  "motion": "Direct AE | Partner-led | AE-led with partner (co-sell)",
  "justification": {{"region": str, "deal_complexity": str, "partner_availability": str, "existing_account_relationship": str}},
  "recommended_partners": [{{"name": str, "type": "System Integrator|Reseller|Distributor|other", "country": str, "evidence": "quote or fact from the text", "role_in_deal": str}}],
  "partner_type_needed": "the partner profile needed if no specific partner fits",
  "roles": {{"flytbase_ae": str, "partner": str, "bdr": str}},
  "risks": [str]
}}"""


def run(lead, qual, case, sources):
    log.stage(5, "Partner identification and GTM motion")
    country = lead["company"].get("country") or ""
    region = lead["company"].get("region") or ""

    log.step("Finding partner pages in the FlytBase sitemap")
    pages = [u for u in tools.sitemap_urls(config.VENDOR_SITE, section_filter=["pages"]) if "partner" in u.lower()]
    pages = sorted(pages, key=len)[:6] or [config.VENDOR_SITE + "/partner"]
    directory = tools.fetch_many(pages, max_chars=20000)
    for u, t in directory.items():
        if t:
            sources.add(u, tools.page_title(u), t, kind="partner_directory")
    log.ok(f"Read {len(pages)} partner page(s)")

    search_hits = []
    for q in [f"FlytBase partner {country}", f"FlytBase {region} drone dock integrator reseller {country}"]:
        log.step(f"search: {q}")
        for r in tools.search(q, max_results=5, depth="basic"):
            search_hits.append(r)
            sources.add(r["url"], r["title"], r["content"], kind="partner_search", query=q)

    partner_text = "\n\n".join(f"[PAGE {u}]\n{t[:12000]}" for u, t in directory.items() if t)
    partner_text += "\n\n" + "\n\n".join(f"[SEARCH {r['url']}] {r['title']}\n{r['content'][:1200]}" for r in search_hits)

    case_info = {k: case.get(k) for k in ("primary", "secondary", "referral_connection", "existing_relationship")}
    # include the full text of any case study involving the lead's own company (may name a partner)
    for p in case.get("pre_scores", []):
        if p.get("mentions_lead_company"):
            src = next((s for s in sources.items.values() if s["url"] == p["url"]), None)
            if src:
                case_info.setdefault("own_company_case_text", []).append(src["content"][:6000])

    result = llm.ask(
        PROMPT.format(
            lead=json.dumps(lead, ensure_ascii=False),
            qual=json.dumps({"summary": qual.get("summary"), "scores": qual.get("scores"), "risks": qual.get("risks")}, ensure_ascii=False),
            case=json.dumps(case_info, ensure_ascii=False),
            partners=partner_text, vendor=config.VENDOR_NAME,
        ),
        temperature=0.1, label="s5_partner",
    )

    # verification: is every recommended partner actually named in a source?
    haystack = (partner_text + " " + json.dumps(case_info, ensure_ascii=False)).lower()
    for p in result.get("recommended_partners", []):
        p["verified_in_sources"] = (p.get("name") or "").lower() in haystack
        if not p["verified_in_sources"]:
            log.warn(f"partner '{p.get('name')}' not found in sources - flagged")
    log.ok(f"Motion: {result.get('motion')}")
    for p in result.get("recommended_partners", []):
        log.ok(f"Partner: {p.get('name')} ({p.get('type')}, {p.get('country')}) verified={p['verified_in_sources']}")
    return result
