"""Stage 3: Adaptive response email sequence. Deterministic part.

The `stage-3-emails` subagent writes the sequence from Stage 1 (the unknowns) and Stage 2 (the cited research).
Python then checks that every email really is tied to both: each one must name the MEDDPICC gaps it targets
(which must be real Stage 1 gaps) and the research it uses (which must be real, kept Stage 2 source IDs).

`writing_checks()` lints the measurable rules of .claude/agents/references/inbound-reply-playbook.md (the rules marked [py]
there): Email 1 length, question count, a CTA with two time options, you-vs-we, follow-ups shorter than Email 1, one link
max, banned phrases and placeholders, subject hygiene, signature, and a close-the-loop final email.
"""
import re


def check_links(emails, qualification, research_ids):
    """Annotate each email with what Python could verify. Returns the list of problems found."""
    gaps = {(m.get("element") or "").lower() for m in qualification.get("missing_information") or []}
    problems = []
    for e in emails.get("emails") or []:
        used = [i for i in e.get("research_used") or [] if re.fullmatch(r"S\d+", str(i))]
        e["research_used_valid"] = [i for i in used if i in research_ids]
        e["gaps_valid"] = [g for g in e.get("meddpicc_gaps_targeted") or [] if g.lower() in gaps]
        bad_ids = sorted(set(used) - set(research_ids))
        if bad_ids:
            problems.append(f"email {e.get('step')}: cites {', '.join(bad_ids)}, which are not in the kept research")
    return problems


# Playbook limits (inbound-reply-playbook.md, sections 2, 3, 6 and 7).
EMAIL1_MAX_WORDS = 200
EMAIL1_MAX_QUESTIONS = 3          # 2 discovery questions + the CTA question
FOLLOWUP_MAX_WORDS = 120
SUBJECT_MAX_WORDS = 8
MAX_LINKS = 1
MAX_I_WE_SENTENCES = 2
SIGNER = "Samruddhi Sontakke"

BANNED_PHRASES = [
    # cold-email openers (they asked us; no apology, no intro)
    "i hope this email finds you well", "hope this finds you well", "my name is", "i came across", "i'm reaching out",
    "i am reaching out", "sorry to bother", "apologies for the intrusion",
    # empty follow-ups
    "just checking in", "checking in to see", "circling back", "bumping this", "did you see my last email", "i never heard back",
    "i know you're busy", "i know you are busy", "quick question", "hope to hear back", "feel free to reach out", "touching base",
    "just following up",
    # buzzwords and hype
    "leverage", "synergy", "best-in-class", "best in class", "seamless", "robust", "unlock", "game-changer", "game changer",
    "cutting-edge", "cutting edge", "revolutionary", "world-class", "act now", "limited time", "don't miss out",
]
_PHRASE_RE = re.compile(r"(?<![a-z])(" + "|".join(re.escape(p) for p in BANNED_PHRASES) + r")(?![a-z])")
_CONTRAST_RE = re.compile(r"\b(?:it'?s|this is|this isn'?t) not (?:just |only )?[^.,;\n]{1,40}[,;] (?:it'?s|but)\b", re.I)
_PLACEHOLDER_RE = re.compile(r"\{\{?[^}]{1,40}\}\}?|\[(?:NEED|TODO|TBD|first.?name|last.?name|name|company|surname|apellido)[^\]]*\]", re.I)
_TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3])(?::[0-5]\d|h[0-5]\d)\b|\b(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s?(?:am|pm|a\.m\.|p\.m\.)", re.I)
_LINK_RE = re.compile(r"https?://|\bwww\.", re.I)
_EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
_CLOSE_LOOP = ["close the loop", "closing the loop", "close this out", "close out", "check back", "hold this", "hold off",
               "pause", "revisit", "reconnect", "right person", "better placed", "someone else", "circle back in",
               "come back to this", "park this", "leave it here"]


def _words(text):
    return len(re.findall(r"[\w'’-]+", text or ""))


def _sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text or "") if x.strip()]


def _count(pattern, text):
    return len(re.findall(pattern, (text or "").lower()))


def lint_email(e):
    """Banned phrases, AI-tell contrast reveals, em dashes and template placeholders found in one email."""
    text = f"{e.get('subject') or ''}\n{e.get('body') or ''}"
    hits = sorted(set(m.lower() for m in _PHRASE_RE.findall(text.lower())))
    if _CONTRAST_RE.search(text):
        hits.append("contrast reveal (it's not X, it's Y)")
    if "\u2014" in text:
        hits.append("em dash")
    hits += [f"placeholder {m}" for m in _PLACEHOLDER_RE.findall(e.get("body") or "")]
    return hits


def writing_checks(em):
    """Deterministic checks for the playbook rules Python can verify. Same item shape as checklist()."""
    emails = list(em.get("emails") or [])
    if not emails:
        return [{"item": "Inbound reply playbook checks", "ok": False, "detail": "no emails"}]
    e1, follow = emails[0], emails[1:]
    b1 = e1.get("body") or ""
    w1 = _words(b1)
    q1 = b1.count("?")
    times = sorted(set(m.strip().lower() for m in _TIME_RE.findall(b1)))
    you = _count(r"\b(?:you|your|yours)\b", b1)
    we = _count(r"\b(?:we|our|ours|us)\b", b1)
    i_we = sum(1 for s in _sentences(b1) if re.match(r"(?:I|We)\b", s))
    fw = [(e.get("step"), _words(e.get("body"))) for e in follow]
    links = [(e.get("step"), len(_LINK_RE.findall(e.get("body") or ""))) for e in emails]
    lint = [(e.get("step"), lint_email(e)) for e in emails]
    subj = [(e.get("step"), e.get("subject") or "") for e in emails]
    bad_subj = [f"email {st}: {s!r}" for st, s in subj
                if not s.strip() or _words(re.sub(r"^\s*re:\s*", "", s, flags=re.I)) > SUBJECT_MAX_WORDS
                or "!" in s or _EMOJI_RE.search(s) or re.match(r"\s*fwd?:", s, re.I)]
    unsigned = [e.get("step") for e in emails if SIGNER.lower() not in (e.get("body") or "").lower()]
    last = (emails[-1].get("body") or "").lower()
    loop_hits = [p for p in _CLOSE_LOOP if p in last]
    return [
        {"item": f"Playbook: Email 1 fits one phone screen (<= {EMAIL1_MAX_WORDS} words)",
         "ok": 0 < w1 <= EMAIL1_MAX_WORDS, "detail": f"{w1} words"},
        {"item": f"Playbook: Email 1 asks at most 2 questions plus the CTA (<= {EMAIL1_MAX_QUESTIONS} '?')",
         "ok": q1 <= EMAIL1_MAX_QUESTIONS, "detail": f"{q1} question marks"},
        {"item": "Playbook: Email 1 CTA offers two specific time options",
         "ok": len(times) >= 2, "detail": ", ".join(times) or "no times found"},
        {"item": "Playbook: Email 1 is about the buyer (you/your >= we/our, <= 2 sentences start with I/We)",
         "ok": you >= we and i_we <= MAX_I_WE_SENTENCES, "detail": f"you {you} vs we {we}; {i_we} I/We sentence starts"},
        {"item": f"Playbook: every follow-up is shorter than Email 1 and <= {FOLLOWUP_MAX_WORDS} words",
         "ok": bool(follow) and all(w < w1 and w <= FOLLOWUP_MAX_WORDS for _, w in fw),
         "detail": "; ".join(f"email {st}: {w} words" for st, w in fw) or "no follow-ups"},
        {"item": f"Playbook: one ask, at most {MAX_LINKS} link per email",
         "ok": all(n <= MAX_LINKS for _, n in links),
         "detail": "; ".join(f"email {st}: {n}" for st, n in links)},
        {"item": "Playbook: no banned phrases, buzzwords, AI tells or placeholders",
         "ok": not any(h for _, h in lint),
         "detail": "; ".join(f"email {st}: {', '.join(h)}" for st, h in lint if h) or "clean"},
        {"item": f"Playbook: subjects describe the content (<= {SUBJECT_MAX_WORDS} words, no '!', emoji or fake Fwd:)",
         "ok": not bad_subj, "detail": "; ".join(bad_subj) or "ok"},
        {"item": "Playbook: every email signed by the named BDR",
         "ok": not unsigned, "detail": f"unsigned: {unsigned}" if unsigned else "ok"},
        {"item": "Playbook: final email closes the loop respectfully",
         "ok": len(emails) >= 2 and bool(loop_hits), "detail": ", ".join(loop_hits) or "no close-the-loop language"},
    ]


def checklist(em):
    emails = em.get("emails") or []
    tone = em.get("tone_adaptation") or {}
    return [
        {"item": "Reflects Stage 2 research (each email cites kept research)",
         "ok": bool(emails) and all(e.get("research_used_valid") for e in emails[:2]),
         "detail": "; ".join(f"email {e.get('step')}: {', '.join(e.get('research_used_valid') or []) or 'none'}" for e in emails)},
        {"item": "Aims to discover the Stage 1 unknowns",
         "ok": bool(emails) and all(e.get("gaps_valid") for e in emails),
         "detail": "; ".join(f"email {e.get('step')}: {', '.join(e.get('gaps_valid') or [])}" for e in emails)},
        {"item": "Tone adapted to seniority, industry and stated context",
         "ok": bool(tone.get("seniority") and tone.get("industry") and tone.get("stated_context"))},
        {"item": "Clear progression logic (why this email, then this email)",
         "ok": bool(em.get("sequence_strategy")) and len(emails) >= 3 and all(e.get("why_this_email_now") for e in emails),
         "detail": f"{len(emails)} emails, {len(em.get('branches') or [])} reply branches"},
    ] + writing_checks(em)
