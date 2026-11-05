"""Stage 6: AE handoff summary. Deterministic part: checks the subagent's handoff against the PDF list and
confirms its research highlights cite sources that survived the Stage 2 fact-check."""


def check_highlights(handoff, research_ids):
    for h in handoff.get("top_3_research_highlights") or []:
        h["source_ids_valid"] = [i for i in h.get("source_ids") or [] if i in research_ids]


def checklist(h):
    b = h.get("buyer_context") or {}
    q = h.get("qualification_status") or {}
    hl = h.get("top_3_research_highlights") or []
    cs = h.get("recommended_case_study") or {}
    ns = h.get("suggested_next_step") or {}
    return [
        {"item": "Buyer context: who he is, what he cares about, who else is involved",
         "ok": bool(b.get("who") and b.get("what_he_cares_about") and b.get("others_involved"))},
        {"item": "Qualification status: framework score, knowns, unknowns",
         "ok": bool(q.get("framework") and q.get("scores") and q.get("knowns") and q.get("unknowns"))},
        {"item": "Top 3 research highlights, each citing kept research",
         "ok": len(hl) == 3 and all(x.get("source_ids_valid") for x in hl)},
        {"item": "Recommended case study and why", "ok": bool(cs.get("title") and cs.get("why"))},
        {"item": "Suggested next step with rationale", "ok": bool(ns.get("action") and ns.get("rationale")),
         "detail": ns.get("action")},
    ]
