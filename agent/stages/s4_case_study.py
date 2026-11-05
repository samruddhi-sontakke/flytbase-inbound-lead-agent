"""Stage 4: Case study and material matching.

1. DISCOVER - read the vendor's sitemap to list every case study (plus a site search as backup).
2. READ     - download every case study page.
3. PRE-SCORE (Python, transparent) - keyword overlap with the lead, plus two flags:
       mentions_referrer      -> the case study names the company that referred the lead
       mentions_lead_company  -> the case study names the lead's OWN company (existing relationship!)
4. RANK (LLM) - the shortlist is judged on industry, use case and operating context.
Nothing about the lead or the referrer is hard-coded: names come from Stage 0.
"""
import json
import re

from .. import config, llm, log, tools

RANK_PROMPT = """You match an inbound lead to the vendor's most relevant customer case study.

LEAD:
{lead}

CASE STUDY SHORTLIST (with automatic flags):
{cases}

Judge each on: industry match, use-case match, operating environment (terrain, climate, scale, 24/7),
geography, and relationship signals (referrer named, or the lead's own company already a customer).
Use only what the case study text says. Return JSON:
{{
  "ranking": [{{"url": str, "title": str, "fit_score": 0-100, "industry_match": str, "use_case_match": str, "context_match": str}}],
  "primary": {{"url": str, "title": str, "source_id": str, "why_strongest_fit": "3-5 sentences", "key_proof_points": ["metric or fact quoted from the page"], "how_to_use_it": "how the BDR/AE should use this in outreach"}},
  "secondary": {{"url": str, "title": str, "why": str}},
  "referral_connection": {{"found": bool, "url": str|null, "explanation": "what the vendor's site shows about the referrer"}},
  "existing_relationship": {{"found": bool, "url": str|null, "source_id": str|null, "explanation": "does the site show the lead's own company already works with the vendor? which operation, which partner, what results?"}},
  "people_named": [{{"name": str, "title": str, "company": str, "source_id": str, "relevance": "why this person matters for this deal"}}]
}}
Copy SOURCE IDs exactly. people_named: only people whose names appear in the case study text of the
lead's own company or of the referrer."""


def _terms(lead):
    words = set()
    for t in lead.get("search_keywords", []) + lead.get("use_cases", []) + [
        lead["company"].get("industry") or "", lead["company"].get("sub_industry") or "",
        lead["company"].get("country") or "", (lead.get("sites") or {}).get("location") or "",
    ]:
        for w in re.findall(r"[a-zA-Z]{4,}", t or ""):
            words.add(w.lower())
    return words


def _names(text):
    """Variants of a company name to search for, e.g. 'Anglo American plc' -> ['anglo american']."""
    if not text:
        return []
    out = {text.lower().strip()}
    out.add(re.sub(r"\(.*?\)", "", text).lower().strip())
    for m in re.findall(r"\(([^)]+)\)", text):
        out.add(m.lower().strip())
    return [n for n in out if len(n) >= 3]


def run(lead, sources):
    log.stage(4, "Case study matching (searching flytbase.com)")
    log.step("Reading the FlytBase sitemap for case studies")
    urls = [u for u in tools.sitemap_urls(config.VENDOR_SITE, section_filter=["case"]) if "/case-stud" in u]
    if not urls:
        log.warn("sitemap gave no case studies, falling back to site search")
    # backup / extra discovery via site search, built from the lead
    queries = [f"{x} case study" for x in (lead.get("referral_source"), lead["company"].get("industry")) if x]
    for q in queries:
        for r in tools.search(q, max_results=5, include_domains=["flytbase.com"], depth="basic"):
            if "/case-stud" in r["url"] and not tools.LANG_PREFIX.match(r["url"]):
                urls.append(r["url"])
    urls = list(dict.fromkeys(urls))
    log.ok(f"Found {len(urls)} case studies")

    log.step("Reading every case study page")
    texts = tools.fetch_many(urls, max_chars=15000)
    # cut the "related stories" footer so one case study's links don't count as a mention in another
    texts = {u: t.split("Related customer stories")[0] for u, t in texts.items()}

    terms = _terms(lead)
    referrer = _names(lead.get("referral_source"))
    own = _names(lead["company"].get("name")) + _names(lead["company"].get("short_name"))
    scored = []
    for u, t in texts.items():
        low = t.lower()
        hits = sorted(w for w in terms if w in low)
        flags = {
            "mentions_referrer": any(re.search(rf"\b{re.escape(n)}\b", low) for n in referrer),
            "mentions_lead_company": any(re.search(rf"\b{re.escape(n)}\b", low) for n in own),
        }
        score = len(hits) + (8 if flags["mentions_referrer"] else 0) + (8 if flags["mentions_lead_company"] else 0)
        scored.append({"url": u, "title": tools.page_title(u), "keyword_hits": hits, "pre_score": score, **flags})
    scored.sort(key=lambda x: x["pre_score"], reverse=True)
    shortlist = [s for s in scored if s["mentions_referrer"] or s["mentions_lead_company"]]
    shortlist += [s for s in scored if s not in shortlist][: max(0, 6 - len(shortlist))]
    for s in shortlist:
        log.step(f"shortlist: {s['title'][:70]} | score {s['pre_score']} | referrer={s['mentions_referrer']} own_company={s['mentions_lead_company']}")

    for s in shortlist:
        s["source_id"] = sources.add(s["url"], s["title"], texts[s["url"]], kind="case_study")
    cases = "\n\n".join(
        f"SOURCE ID: {s['source_id']}\nURL: {s['url']}\nTITLE: {s['title']}\nFLAGS: mentions_referrer={s['mentions_referrer']}, "
        f"mentions_lead_company={s['mentions_lead_company']}\nTEXT: {texts[s['url']][:4000]}"
        for s in shortlist
    )
    result = llm.ask(RANK_PROMPT.format(lead=json.dumps(lead, ensure_ascii=False), cases=cases),
                     temperature=0.1, label="s4_case_study")
    result["pre_scores"] = scored
    result["case_studies_scanned"] = len(urls)
    log.ok(f"Primary match: {result.get('primary', {}).get('title')}")
    if result.get("existing_relationship", {}).get("found"):
        log.ok("ALERT: the lead's own company already appears in a FlytBase case study")
    return result
