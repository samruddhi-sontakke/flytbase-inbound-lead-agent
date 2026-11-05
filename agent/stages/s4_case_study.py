"""Stage 4: Case study and material matching. Deterministic part.

1. DISCOVER (Python) - read the vendor's sitemap to list every case study; the subagent can add more URLs it
                       found with WebSearch (site:flytbase.com).
2. READ     (Python) - download every case study page.
3. PRE-SCORE (Python, transparent) - keyword overlap with the lead, plus two flags:
       mentions_referrer      -> the case study names the company that referred the lead
       mentions_lead_company  -> the case study names the lead's OWN company (existing relationship!)
4. RANK (subagent `stage-4-case-study`) - judges the shortlist on industry, use case and operating context.
Nothing about the lead or the referrer is hard-coded: names come from the Stage 1 intake.
"""
import re

from .. import config, tools


def _terms(lead):
    words = set()
    co = lead.get("company") or {}
    for t in (lead.get("search_keywords") or []) + (lead.get("use_cases") or []) + [
        co.get("industry") or "", co.get("sub_industry") or "", co.get("country") or "",
        (lead.get("sites") or {}).get("location") or "",
    ]:
        for w in re.findall(r"[a-zA-Z]{4,}", t or ""):
            words.add(w.lower())
    return words


def _names(text):
    """Variants of a company name to search for, e.g. 'Sociedad X (SQM)' -> ['sociedad x (sqm)', 'sociedad x', 'sqm']."""
    if not text:
        return []
    out = {text.lower().strip(), re.sub(r"\(.*?\)", "", text).lower().strip()}
    for m in re.findall(r"\(([^)]+)\)", text):
        out.add(m.lower().strip())
    return [n for n in out if len(n) >= 3]


def discover(extra_urls=None):
    urls = [u for u in tools.sitemap_urls(config.VENDOR_SITE, section_filter=["case"]) if "/case-stud" in u]
    from_sitemap = len(urls)
    for u in extra_urls or []:
        if "flytbase.com" in u and "/case-stud" in u and not tools.LANG_PREFIX.match(u):
            urls.append(u)
    return list(dict.fromkeys(urls)), from_sitemap


def prescore(lead, texts):
    terms = _terms(lead)
    co = lead.get("company") or {}
    referrer = _names(lead.get("referral_source"))
    own = _names(co.get("name")) + _names(co.get("short_name"))
    scored = []
    for u, t in texts.items():
        low = (t or "").lower()
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
    return scored, shortlist, {"keyword_terms": sorted(terms), "referrer_names": referrer, "own_company_names": own}


def checklist(c):
    primary = c.get("primary") or {}
    ranking = c.get("ranking") or []
    ref = c.get("referral_connection") or {}
    return [
        {"item": "Autonomously searched FlytBase's public website for case studies", "ok": (c.get("case_studies_scanned") or 0) > 0,
         "detail": f"{c.get('case_studies_scanned')} case studies scanned"},
        {"item": "Referral connection identified (no hard-coding)", "ok": bool(ref.get("explanation")),
         "detail": f"found={ref.get('found')} {ref.get('url') or ''}"},
        {"item": "Matched on industry, use case and operational context",
         "ok": bool(ranking) and all(r.get("industry_match") and r.get("use_case_match") and r.get("context_match") for r in ranking[:3])},
        {"item": "Explains why the case study is the strongest fit", "ok": bool(primary.get("why_strongest_fit")),
         "detail": primary.get("title")},
        {"item": "Primary match is a page the crawler actually read", "ok": bool(primary.get("url_verified"))},
    ]
