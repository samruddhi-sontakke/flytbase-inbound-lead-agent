"""Stage 2: Deep account research. Deterministic part.

Flow (each step inspectable):
  1. PLAN + GATHER  - the `stage-2-research` subagent plans queries across the PDF categories, finds sources
                      with WebSearch / Reddit / LinkedIn, and registers each one through the MCP tools
                      `read_page` / `register_source`, which store the raw text and return an ID like S7.
  2. WRITE          - the subagent writes the brief, citing only those IDs, and saves it as a draft.
  3. VERIFY         - a separate `research-fact-checker` subagent gets every claim plus the stored text of the
                      sources it cites (built here by `claims_for_check`) and returns a verdict per claim.
  4. APPLY (Python) - `apply_fact_check` removes unsupported claims and claims citing unknown IDs, and records them.
"""

CATEGORIES = {
    "org_structure": "organisational structure, divisions, executives and reporting lines relevant to the contact",
    "budget_signals": "capex / opex guidance, investment plans, technology or automation spend from annual reports, 20-F or results",
    "recent_news": "news, press releases and strategic announcements from the last 12-18 months",
    "investor_priorities": "shareholder / investor letters, earnings calls, sustainability reports that reveal operational priorities",
    "operations_context": "the specific sites, operations, safety and workforce context mentioned in the lead",
    "technology_adoption": "drones, automation, digital innovation or remote operations already used by the company",
}

FINDING_LISTS = ["company_snapshot", "budget_signals", "recent_news", "investor_priorities",
                 "operations_context", "technology_adoption"]


def _collect(brief):
    """Yield (path, finding) for every cited claim in the brief, in a stable order."""
    for key in FINDING_LISTS:
        for f in brief.get(key) or []:
            yield key, f
    org = brief.get("org_structure") or {}
    for f in org.get("findings") or []:
        yield "org_structure", f
    for p in org.get("relevant_stakeholders") or []:
        yield "stakeholders", p


def _claim_text(path, f):
    if path == "stakeholders":
        return f"{f.get('name')} is {f.get('title')}"
    return f.get("claim") or ""


def _passages(claim, text, max_chars=3500, window=700):
    """The parts of a long source that matter for one claim: the opening, plus the windows that contain the
    claim's numbers and names. Long filings put the key figure deep in the text, so the first N characters
    are not enough (a fact-checker given only the table of contents would wrongly reject true claims)."""
    import re
    text = text or ""
    if len(text) <= max_chars:
        return text
    terms = set(re.findall(r"\d[\d.,]*\d|\d", claim))
    terms |= {w for w in re.findall(r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ]{3,}", claim)}
    terms |= {w for w in re.findall(r"[a-záéíóúñ]{7,}", claim.lower())}
    low = text.lower()
    hits = []
    for t in terms:
        start = 0
        while True:
            i = low.find(t.lower(), start)
            if i < 0:
                break
            hits.append(i)
            start = i + 1
    # score each window by how many distinct terms it contains, keep the best non-overlapping ones
    scored = []
    for h in set(hits):
        a = max(0, h - window // 2)
        chunk = low[a:a + window]
        scored.append((sum(1 for t in terms if t.lower() in chunk), a))
    scored.sort(reverse=True)
    picked = []
    for _, a in scored:
        if all(abs(a - b) >= window for b in picked):
            picked.append(a)
        if (len(picked) + 1) * window >= max_chars:
            break
    parts = [text[:window]] + [f"[... at char {a} ...] " + text[a:a + window] for a in sorted(picked)]
    return "\n".join(parts)


def claims_for_check(brief, get_source, max_chars=3500):
    """Numbered claims with the relevant passages of their cited sources, for the fact-checker subagent.
    The checker can read any source in full with get_sources(ids, max_chars=60000) if a passage is not enough."""
    items = []
    for n, (path, f) in enumerate(_collect(brief), start=1):
        ids = [i for i in f.get("source_ids") or [] if get_source(i)]
        claim = _claim_text(path, f)
        items.append({
            "n": n, "section": path, "claim": claim, "source_ids": f.get("source_ids") or [],
            "cited_text": {i: _passages(claim, get_source(i).get("content") or "", max_chars) for i in ids[:3]},
            "source_length": {i: len(get_source(i).get("content") or "") for i in ids[:3]},
            "auto_unsupported": not ids,
        })
    return items


def apply_fact_check(brief, verdicts, get_source):
    """Copy each verdict onto its claim, then drop unsupported ones. Claims that cite no valid stored
    source are unsupported no matter what the checker said."""
    by_n = {int(v.get("n", 0)): v for v in verdicts or []}
    found = list(_collect(brief))
    for n, (path, f) in enumerate(found, start=1):
        valid = [i for i in f.get("source_ids") or [] if get_source(i)]
        v = by_n.get(n) or {}
        if not valid:
            f["verification"], f["verification_note"] = "unsupported", "no valid stored source cited"
        else:
            f["verification"] = v.get("verdict") if v.get("verdict") in ("supported", "partial", "unsupported") else "unsupported"
            f["verification_note"] = v.get("note") or ("not checked" if not v else "")
    removed = []

    def keep(items):
        out = []
        for f in items or []:
            (removed.append(f) if f.get("verification") == "unsupported" else out.append(f))
        return out

    for key in FINDING_LISTS:
        brief[key] = keep(brief.get(key))
    org = brief.setdefault("org_structure", {})
    org["findings"] = keep(org.get("findings"))
    people = []
    for p in org.get("relevant_stakeholders") or []:
        if p.get("verification") == "unsupported":
            removed.append({"claim": f"{p.get('name')} is {p.get('title')}", "source_ids": p.get("source_ids"),
                            "verification": "unsupported", "verification_note": p.get("verification_note")})
        else:
            people.append(p)
    org["relevant_stakeholders"] = people
    brief["removed_by_fact_check"] = removed
    brief["fact_check"] = {"claims_checked": len(found), "removed": len(removed),
                           "partial": sum(1 for _, f in _collect(brief) if f.get("verification") == "partial")}
    return brief


def checklist(r):
    org = r.get("org_structure") or {}
    pos = r.get("positioning_recommendation") or {}
    cited = all(f.get("source_ids") for _, f in _collect(r))
    return [
        {"item": "Organizational structure and reporting lines", "ok": bool(org.get("findings") or org.get("relevant_stakeholders")),
         "detail": org.get("likely_reporting_line")},
        {"item": "Budget signals from public filings (capex, opex, technology)", "ok": bool(r.get("budget_signals"))},
        {"item": "Recent news, press releases, strategic announcements", "ok": bool(r.get("recent_news"))},
        {"item": "Stakeholder or investor letters revealing priorities", "ok": bool(r.get("investor_priorities"))},
        {"item": "Synthesized FlytBase positioning recommendation", "ok": bool(pos.get("summary"))},
        {"item": "All research real: every kept claim cites a stored source and passed the fact-check", "ok": cited,
         "detail": f"{(r.get('fact_check') or {}).get('claims_checked', 0)} claims checked, "
                   f"{(r.get('fact_check') or {}).get('removed', 0)} removed"},
    ]
