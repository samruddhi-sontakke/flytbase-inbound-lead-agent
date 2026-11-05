"""Turns the six stage outputs (JSON) into one readable report: REPORT.md and REPORT.html.
Pure formatting - no AI here. Every [S#] citation becomes a clickable link to its source."""
import re


def _cite(text, sources):
    if not isinstance(text, str):
        return text

    def rep(m):
        ids = re.findall(r"S\d+", m.group(0))
        links = [f"[{i}]({sources.get(i)['url']})" if sources.get(i) else i for i in ids]
        return "[" + ", ".join(links) + "]"
    return re.sub(r"\[(S\d+(?:\s*,\s*S\d+)*)\](?!\()", rep, text)


def _ids(ids, sources, text=""):
    ids = [i for i in (ids or []) if f"{i}]" not in (text or "") and f"{i}," not in (text or "")]
    return " " + _cite("[" + ", ".join(ids) + "]", sources) if ids else ""


def _findings(title, items, sources):
    out = [f"\n**{title}**\n"]
    if not items:
        out.append("- _Nothing verified in public sources._")
    for f in items or []:
        flag = " _(partially verified)_" if f.get("verification") == "partial" else ""
        out.append(f"- {_cite(f.get('claim'), sources)}{_ids(f.get('source_ids'), sources, f.get('claim'))}{flag}")
        if f.get("so_what"):
            out.append(f"  - _So what:_ {f['so_what']}")
    return out


def build(run, sources):
    lead, q, r, case, p, em, h = (run[k] for k in ("lead", "qualification", "research", "case_study", "partner", "emails", "handoff"))
    c, co = lead["contact"], lead["company"]
    L = []
    a = L.append
    a(f"# Inbound Lead Report: {c.get('name')} - {co.get('name')}")
    a(f"_Generated automatically by the Inbound Lead Desk agent (Claude Code, one subagent per stage) on {run['meta']['started']} "
      f"in {run['meta']['seconds']}s ({run['meta']['llm_calls']} subagent calls, {len(sources.items)} sources). "
      f"Every research fact links to its source._\n")
    a(f"> **{h.get('one_line_summary', '')}**\n")
    checks = [(n, t, (run.get(k) or {}).get("pdf_checklist")) for n, t, k in (
        (1, "Qualification", "qualification"), (2, "Deep account research", "research"), (3, "Response generation", "emails"),
        (4, "Case study matching", "case_study"), (5, "Partner identification", "partner"), (6, "AE handoff", "handoff"))]
    if any(c for _, _, c in checks):
        a("## Assignment requirements check\n_Each requirement in the assignment PDF, checked in Python against the stage output._\n")
        a("| Stage | Requirement | Met |\n|---|---|---|")
        for n, t, c in checks:
            for x in c or []:
                a(f"| {n} {t} | {x['item']}{' (' + str(x['detail']) + ')' if x.get('detail') else ''} | {'yes' if x['ok'] else '**no**'} |")
        a("")

    # ---------- Stage 1
    s = q["scores"]
    a("## Stage 1 - Qualification (MEDDPICC)")
    a(f"**Why MEDDPICC:** {q.get('framework_rationale')}\n")
    a(f"| ICP fit | MEDDPICC completeness | Priority score | Tier |\n|---|---|---|---|\n"
      f"| {s['icp_fit_score']}/100 | {s['meddpicc_completeness']}% | **{s['priority_score']}/100** | {s['priority_tier']} |\n")
    a(f"_Formula: {s['formula']}_\n")
    a("| Element | Status | Known from email | Missing | Discovery question |\n|---|---|---|---|---|")
    for e in q.get("elements", []):
        a(f"| {e.get('name')} | {e.get('status')} | {e.get('evidence') or '-'} | {e.get('missing') or '-'} | {e.get('discovery_question') or '-'} |")
    a("\n**Fit assessment**\n\n| Factor | Weight | Rating (0-5) | Reason |\n|---|---|---|---|")
    for k, w in q.get("fit_weights", {}).items():
        fr = q.get("fit_ratings", {}).get(k, {})
        a(f"| {k} | {w} | {fr.get('rating')} | {fr.get('reason')} |")
    a(f"\n**Verdict:** {q.get('summary')}\n")
    if q.get("risks"):
        a("**Risks:** " + "; ".join(q["risks"]) + "\n")

    # ---------- Stage 2
    a("## Stage 2 - Deep Account Research")
    org = r.get("org_structure", {})
    L += _findings("Organisational structure", org.get("findings"), sources)
    if org.get("relevant_stakeholders"):
        a("\n**Stakeholders found in public sources**\n")
        for pp in org["relevant_stakeholders"]:
            a(f"- **{pp.get('name')}**, {pp.get('title')} - {_cite(pp.get('why_relevant'), sources)}{_ids(pp.get('source_ids'), sources, pp.get('why_relevant'))}")
    if org.get("likely_reporting_line"):
        a(f"\n_Likely reporting line (inference):_ {_cite(org['likely_reporting_line'], sources)}")
    L += _findings("Budget signals (capex / opex / technology)", r.get("budget_signals"), sources)
    L += _findings("Recent news and announcements", r.get("recent_news"), sources)
    L += _findings("Investor / stakeholder priorities", r.get("investor_priorities"), sources)
    L += _findings("Operations context", r.get("operations_context"), sources)
    L += _findings("Technology and drone adoption", r.get("technology_adoption"), sources)
    pr = r.get("positioning_recommendation", {})
    a(f"\n**Positioning recommendation:** {_cite(pr.get('summary'), sources)}\n")
    for x in pr.get("angles", []):
        a(f"- {_cite(x, sources)}")
    if pr.get("risks_or_objections"):
        a("\n_Likely objections:_ " + "; ".join(pr["risks_or_objections"]))
    if r.get("not_found"):
        a("\n_Searched for but not found:_ " + "; ".join(r["not_found"]))
    rem = r.get("removed_by_fact_check", [])
    a(f"\n_Fact-check: {len(rem)} claim(s) were removed because the cited source did not support them._\n")

    # ---------- Stage 3
    a("## Stage 3 - Adaptive Email Sequence")
    a(f"**Strategy:** {em.get('sequence_strategy')}\n")
    for e in em.get("emails", []):
        a(f"### Email {e.get('step')} - {e.get('send_when')}")
        a(f"**Goal:** {e.get('goal')}  \n**Gaps targeted:** {', '.join(e.get('meddpicc_gaps_targeted', []))}  \n"
          f"**Why this email now:** {e.get('why_this_email_now')}  \n**Success signal:** {e.get('success_signal')}"
          f"{'  ' + chr(10) + '**Research used:**' + _ids(e.get('research_used'), sources) if e.get('research_used') else ''}\n")
        a(f"**Subject:** {e.get('subject')}\n")
        a("```text\n" + (e.get("body") or "") + "\n```\n")
    if em.get("branches"):
        a("**Branches (adapt to his reply)**\n")
        for b in em["branches"]:
            a(f"- **If he replies:** {b.get('if_reply')}  \n  **Then:** {b.get('next_action')}")
            if b.get("draft_reply"):
                a("\n  ```text\n  " + b["draft_reply"].replace("\n", "\n  ") + "\n  ```")

    # ---------- Stage 4
    a("\n## Stage 4 - Case Study Match")
    pm = case.get("primary", {})
    a(f"_Scanned {case.get('case_studies_scanned')} case studies on flytbase.com._\n")
    a(f"**Best match:** [{pm.get('title')}]({pm.get('url')})\n\n{pm.get('why_strongest_fit')}\n")
    for x in pm.get("key_proof_points", []):
        a(f"- {x}")
    a(f"\n**How to use it:** {pm.get('how_to_use_it')}\n")
    sm = case.get("secondary", {})
    if sm:
        a(f"**Runner-up:** [{sm.get('title')}]({sm.get('url')}) - {sm.get('why')}\n")
    rc, er = case.get("referral_connection", {}), case.get("existing_relationship", {})
    a(f"**Referral connection ({lead.get('referral_source')}):** {rc.get('explanation')} {('[link](' + rc['url'] + ')') if rc.get('url') else ''}\n")
    a(f"**Existing relationship with {co.get('short_name') or co.get('name')}:** {er.get('explanation')} {('[link](' + er['url'] + ')') if er.get('url') else ''}\n")
    if case.get("people_named"):
        a("**People named on FlytBase's site (warm contacts)**\n")
        for x in case["people_named"]:
            a(f"- **{x.get('name')}**, {x.get('title')}, {x.get('company')} - {x.get('relevance')}{_ids([x.get('source_id')] if x.get('source_id') else [], sources)}")
        a("")
    a("| Case study | Fit | Industry | Use case | Context |\n|---|---|---|---|---|")
    for x in case.get("ranking", []):
        a(f"| [{x.get('title')}]({x.get('url')}) | {x.get('fit_score')} | {x.get('industry_match')} | {x.get('use_case_match')} | {x.get('context_match')} |")

    # ---------- Stage 5
    a("\n## Stage 5 - Partner & Go-to-Market Motion")
    a(f"**Recommended motion:** {p.get('motion')}\n")
    for k, v in (p.get("justification") or {}).items():
        a(f"- **{k.replace('_', ' ').title()}:** {v}")
    if p.get("recommended_partners"):
        a("\n| Partner | Type | Country | Evidence | Role in deal | Verified in sources |\n|---|---|---|---|---|---|")
        for x in p["recommended_partners"]:
            a(f"| {x.get('name')} | {x.get('type')} | {x.get('country')} | {x.get('evidence')} | {x.get('role_in_deal')} | {'yes' if x.get('verified_in_sources') else 'NO - check'} |")
    a(f"\n**Partner profile needed:** {p.get('partner_type_needed')}\n")
    for k, v in (p.get("roles") or {}).items():
        a(f"- **{k}:** {v}")

    # ---------- Stage 6
    a("\n## Stage 6 - AE Handoff Summary")
    bc = h.get("buyer_context", {})
    a(f"**Buyer:** {bc.get('who')}\n\n**What he cares about:**")
    for x in bc.get("what_he_cares_about", []):
        a(f"- {x}")
    a("\n**Others likely involved:**")
    for x in bc.get("others_involved", []):
        a(f"- {x.get('name_or_role')} - {x.get('why')}")
    qs = h.get("qualification_status", {})
    a(f"\n**Qualification:** {qs.get('framework')} - {qs.get('scores')}  \n**Knowns:** {'; '.join(qs.get('knowns', []))}  \n**Unknowns:** {'; '.join(qs.get('unknowns', []))}\n")
    a("**Top 3 research highlights**")
    for x in h.get("top_3_research_highlights", []):
        a(f"1. {_cite(x.get('finding'), sources)}{_ids(x.get('source_ids'), sources, x.get('finding'))} - _{x.get('why_ae_should_care')}_")
    rcs = h.get("recommended_case_study", {})
    a(f"\n**Case study:** [{rcs.get('title')}]({rcs.get('url')}) - {rcs.get('why')}\n")
    a(f"**GTM motion:** {h.get('gtm_motion')}\n")
    ns = h.get("suggested_next_step", {})
    a(f"**Next step:** {ns.get('action')} (owner: {ns.get('owner')}, by: {ns.get('by_when')})  \n_Why:_ {ns.get('rationale')}\n")
    if h.get("watch_outs"):
        a("**Watch-outs:** " + "; ".join(h["watch_outs"]) + "\n")

    # ---------- Sources
    a("\n## Sources")
    for sid, src in sources.items.items():
        a(f"- **{sid}** [{src['title']}]({src['url']}) _({src['kind']})_")
    return _cite("\n".join(L), sources)


def to_html(md_text, title):
    try:
        import markdown
        body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    except ImportError:
        import html
        body = "<pre>" + html.escape(md_text) + "</pre>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;max-width:980px;margin:32px auto;padding:0 16px;line-height:1.55;color:#1d2433}}
h1{{color:#0b3d91}}h2{{border-bottom:2px solid #e3e8f0;padding-bottom:6px;margin-top:40px;color:#0b3d91}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0}}td,th{{border:1px solid #d5dbe5;padding:6px 8px;vertical-align:top}}
th{{background:#f2f5fa}}pre{{background:#f6f8fb;padding:12px;border-radius:6px;white-space:pre-wrap}}
blockquote{{border-left:4px solid #0b3d91;margin:0;padding:8px 16px;background:#f2f5fa}}a{{color:#0b57d0}}</style>
</head><body>{body}</body></html>"""
