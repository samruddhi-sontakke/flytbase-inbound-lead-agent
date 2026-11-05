"""Stage 5: Partner identification and go-to-market motion. Deterministic part.

1. DISCOVER (Python) - find the vendor's partner pages in its sitemap and read them.
2. SEARCH   (subagent) - WebSearch for vendor partners in the lead's country / region; pages registered as sources.
3. DECIDE   (subagent `stage-5-partner`) - direct AE vs partner-led, from region, deal complexity, partner availability.
4. VERIFY   (Python) - every partner the subagent names must appear in the stored text of this lead's sources.
"""
from .. import config, tools

MOTIONS = ("Direct AE", "Partner-led", "AE-led with partner (co-sell)")


def partner_pages():
    pages = [u for u in tools.sitemap_urls(config.VENDOR_SITE, section_filter=["pages"]) if "partner" in u.lower()]
    return sorted(pages, key=len)[:6] or [config.VENDOR_SITE + "/partner"]


def verify(partner, all_source_text):
    hay = (all_source_text or "").lower()
    for p in partner.get("recommended_partners") or []:
        p["verified_in_sources"] = bool(p.get("name")) and p["name"].lower() in hay
    return [p.get("name") for p in partner.get("recommended_partners") or [] if not p.get("verified_in_sources")]


def checklist(p):
    j = p.get("justification") or {}
    partners = p.get("recommended_partners") or []
    partner_led = "partner" in (p.get("motion") or "").lower()
    return [
        {"item": "Direct AE or partner-led motion for the region decided", "ok": p.get("motion") in MOTIONS, "detail": p.get("motion")},
        {"item": "Justified by region, deal complexity and partner availability",
         "ok": bool(j.get("region") and j.get("deal_complexity") and j.get("partner_availability"))},
        {"item": "If partner-led: specific partner type and rationale",
         "ok": (not partner_led) or bool((partners and all(x.get("type") and x.get("role_in_deal") for x in partners)) or p.get("partner_type_needed")),
         "detail": ", ".join(f"{x.get('name')} ({x.get('type')})" for x in partners)},
        {"item": "Every named partner appears in a stored source", "ok": all(x.get("verified_in_sources") for x in partners)},
    ]
