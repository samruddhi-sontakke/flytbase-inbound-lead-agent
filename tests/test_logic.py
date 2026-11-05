"""Deterministic logic: scoring, fact-check removal, partner verification, inbox markers, checklists.  py -m pytest tests"""
from agent import store
from agent.stages import s1_qualify, s2_research, s3_emails, s4_case_study, s5_partner


def _qual(rating=5, status="known"):
    return {"elements": [{"key": k, "name": n, "status": status} for k, n, _ in s1_qualify.ELEMENTS],
            "fit_ratings": {f: {"rating": rating, "reason": "x"} for f in s1_qualify.FIT_FACTORS}}


def test_score_bounds_and_tiers():
    top = s1_qualify.score(_qual(5, "known"))
    assert top["icp_fit_score"] == 100 and top["meddpicc_completeness"] == 100 and top["priority_score"] == 100
    assert top["priority_tier"].startswith("P1")
    low = s1_qualify.score(_qual(1, "unknown"))
    assert low["icp_fit_score"] == 20 and low["priority_tier"].startswith("P3")
    assert s1_qualify.score(_qual(9))["icp_fit_score"] == 100  # ratings are clamped to 0-5


def test_validate_catches_missing_elements():
    data = _qual()
    data["elements"] = data["elements"][:3]
    problems = s1_qualify.validate(data)
    assert any("lead." in p for p in problems) and any("Paper Process" in p for p in problems)


def test_fact_check_removes_unsupported_and_unsourced():
    brief = {"budget_signals": [{"claim": "a", "source_ids": ["S1"]}, {"claim": "b", "source_ids": ["S2"]},
                                {"claim": "c", "source_ids": ["S99"]}],
             "org_structure": {"relevant_stakeholders": [{"name": "X", "title": "CEO", "source_ids": ["S1"]}]}}
    srcs = {"S1": {"content": "a"}, "S2": {"content": "b"}}
    out = s2_research.apply_fact_check(brief, [{"n": 1, "verdict": "supported"}, {"n": 2, "verdict": "unsupported"},
                                               {"n": 3, "verdict": "supported"}, {"n": 4, "verdict": "partial"}], srcs.get)
    assert [f["claim"] for f in out["budget_signals"]] == ["a"]
    assert len(out["removed_by_fact_check"]) == 2  # b (checker said no) and c (cites a source that doesn't exist)
    assert out["org_structure"]["relevant_stakeholders"][0]["verification"] == "partial"


def test_partner_verification():
    p = {"recommended_partners": [{"name": "Adentu"}, {"name": "Made Up Drones"}]}
    assert s5_partner.verify(p, "Deployed with ADENTU in Chile") == ["Made Up Drones"]


def test_email_links_checked():
    q = {"missing_information": [{"element": "Economic Buyer"}]}
    em = {"emails": [{"step": 1, "research_used": ["S1", "S7"], "meddpicc_gaps_targeted": ["Economic Buyer", "Made up"]}]}
    problems = s3_emails.check_links(em, q, {"S1"})
    assert em["emails"][0]["research_used_valid"] == ["S1"] and em["emails"][0]["gaps_valid"] == ["Economic Buyer"]
    assert problems and "S7" in problems[0]


def test_prescore_flags_referrer_without_hardcoding():
    lead = {"company": {"name": "Acme Mining (ACM)", "short_name": "ACM", "industry": "mining"},
            "referral_source": "Bigco Resources", "search_keywords": ["copper", "inspection"]}
    texts = {"https://flytbase.com/case-study/a": "Bigco Resources runs copper inspection",
             "https://flytbase.com/case-study/b": "solar farm security"}
    scored, shortlist, _ = s4_case_study.prescore(lead, texts)
    assert scored[0]["url"].endswith("/a") and scored[0]["mentions_referrer"] and not scored[1]["mentions_referrer"]


def test_inbox_markers():
    form = ("Source: flytbase.com/contact\nFrom: Jane (jane@acme-mining.com)\nTitle: COO\nCompany: Acme\n"
            "Subject: Drone inspection\nContext: need autonomous inspection")
    hits, score = store._markers("forms@site.com", "New contact form", form)
    assert hits["contact_form_source"] and hits["business_email_domain"] and score >= 6
    hits, score = store._markers("news@shop.com", "Sale", "50% off everything. Unsubscribe here.")
    assert score < 3


# --- Stage 3 writing checks (inbound-reply-playbook.md rules marked [py]) ---
_SIG = "\n\nSamruddhi Sontakke\nBusiness Development, FlytBase"


def _good_sequence():
    e1 = ("Dear Ms. Rojas,\n\nThank you for your note about drone operations across your three lithium sites, and for "
          "mentioning the Anglo American introduction. Running 24/7 inspection without sending crews into hazardous areas "
          "ahead of your Q3 budget review is exactly the problem your team described.\n\n"
          "One relevant example: a mining operator uses docked drones for routine site inspection across remote pits.\n\n"
          "Two questions so the call is useful: which site would you pilot first, and who else joins the budget decision?\n\n"
          "Would Tuesday 10:00 or Wednesday 15:00 Santiago time work for a 30-minute call? Con gusto podemos continuar en español." + _SIG)
    f1 = "Dear Ms. Rojas,\n\nA short note on permits: here is how docked operations are typically approved for remote sites. Does Tuesday 10:00 still suit?" + _SIG
    f2 = "Dear Ms. Rojas,\n\nHere is a five-point summary you can forward to your safety and IT colleagues. Is a short call next week still useful?" + _SIG
    f3 = "Dear Ms. Rojas,\n\nShould I hold this until your Q3 budget review, or is someone else at your team better placed to talk?" + _SIG
    return {"emails": [{"step": i + 1, "subject": "Re: drone operations for your lithium sites", "body": b}
                       for i, b in enumerate([e1, f1, f2, f3])]}


def test_writing_checks_pass_on_good_inbound_sequence():
    checks = s3_emails.writing_checks(_good_sequence())
    assert len(checks) == 10
    assert all(c["ok"] for c in checks), [c for c in checks if not c["ok"]]


def test_checklist_keeps_pdf_items_and_appends_playbook():
    items = [c["item"] for c in s3_emails.checklist(_good_sequence())]
    assert items[0].startswith("Reflects Stage 2 research") and items[3].startswith("Clear progression logic")
    assert len(items) == 14 and all(i.startswith("Playbook:") for i in items[4:])


def test_writing_checks_catch_long_email1_too_many_questions_and_no_times():
    em = _good_sequence()
    em["emails"][0]["body"] = ("word " * 230) + "A? B? C? D? Let me know when works." + _SIG
    by = {c["item"]: c["ok"] for c in s3_emails.writing_checks(em)}
    assert not next(v for k, v in by.items() if "phone screen" in k)
    assert not next(v for k, v in by.items() if "questions" in k)
    assert not next(v for k, v in by.items() if "time options" in k)


def test_writing_checks_catch_banned_phrases_placeholders_and_em_dash():
    em = _good_sequence()
    em["emails"][1]["body"] = "Just checking in — our seamless platform. Hi {first_name}, [NEED: proof]" + _SIG
    lint = s3_emails.lint_email(em["emails"][1])
    assert "just checking in" in lint and "seamless" in lint and "em dash" in lint
    assert any("first_name" in h for h in lint) and any("NEED" in h for h in lint)
    assert not next(c for c in s3_emails.writing_checks(em) if "banned" in c["item"])["ok"]
    assert s3_emails.lint_email({"body": "It's not a drone, it's a system."})


def test_writing_checks_followups_shorter_close_loop_subject_signature_links():
    em = _good_sequence()
    em["emails"][2]["body"] = em["emails"][0]["body"] + " Extra."
    em["emails"][3]["body"] = "Here is another case study for you: https://a.example and https://b.example"
    em["emails"][1]["subject"] = "Fwd: AMAZING OFFER for you today only!!"
    by = {c["item"]: c for c in s3_emails.writing_checks(em)}
    get = lambda key: next(c for k, c in by.items() if key in k)
    assert not get("shorter than Email 1")["ok"]
    assert not get("closes the loop")["ok"]
    assert not get("subjects")["ok"]
    assert not get("signed")["ok"] and "4" in get("signed")["detail"]
    assert not get("link")["ok"]


def test_writing_checks_about_buyer_and_empty():
    em = _good_sequence()
    em["emails"][0]["body"] = "We built this. We are great. We have docks. Our team ships. Tuesday 10:00 or 15:00?" + _SIG
    assert not next(c for c in s3_emails.writing_checks(em) if "about the buyer" in c["item"])["ok"]
    assert s3_emails.writing_checks({})[0]["ok"] is False
