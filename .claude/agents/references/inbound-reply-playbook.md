# Inbound Reply Playbook (Stage 3 source of truth)

Stage 3 (`stage-3-emails`) reads this before writing. Python checks the measurable rules (marked **[py]**) in
`agent/stages/s3_emails.py` `checklist()`. Each rule names its source, and the source list is at the bottom.
Claims the research could not verify (speed-to-lead multipliers, vendor reply-rate benchmarks, self-reported results)
are left out on purpose.

## 1. Core philosophy: this is inbound, not cold

- **They asked us.** The lead filled the flytbase.com contact form and asked for help. Email 1 is anticipated, so don't
  apologise, don't try to "earn permission" and don't use cold-email hooks. [Godin, Permission Marketing][g1]
- **The permission covers only what they asked about.** It's permission to reply about their request, not to pitch
  other products or add them to a newsletter or list. "Signing up for A is not permission for B." [Godin][g1], [Godin, Ouch][g2]
- **About them, not us.** No company bio and no "we are the leading...". About 75-80% of the email is about the buyer.
  [Godin, Seven marketing sins][g3], [Lopuch, WARM][l3], [Berman][b1]
- **Relevance over personalisation.** Every personal line ties a researched fact to the buyer's goal, such as safe crews,
  uptime across sites, or a business case that makes them look good at budget time. Leave out trivia. [Lopuch, Copy Hackers][l1], [marketingskills cold-email][m1]
- **Generosity builds trust.** Each email should help even if they never book. Exaggeration destroys that trust, so
  never invent customers, numbers, integrations or quotes. [Godin, Deconstructing generosity][g4], [marketingskills copywriting][m3]
- **Speed and relevance together.** Draft Email 1 within minutes of the sweep so the BDR can send it the same
  business hour (Tier 1 SLA: 1 hour). A fast generic auto-reply hurts serious buyers. If research isn't finished, write a short
  acknowledgement with one specific next step rather than a template. [marketingskills revops routing][m6], [Yesware][y1]
  (The InsideSales/Oldroyd lead-response study [s1] points the same way. It measured phone calls, so treat it as directional only.)
- **Peer proof.** "People like us do things like this." A verified peer deployment (mining, heavy industry, the referrer)
  persuades an operations head more than features do. [Godin, Levels interview][g5]
- **Write for one buyer.** Aim at this person's role and problem, not at "mining companies". [Godin, smallest viable audience][g6]

## 2. The first reply (Email 1)

**Structure** (WARM, adapted from [Lopuch][l3] and [Berman, 3Cs][b6], using the inbound slot order):
1. **Greeting**, formal for senior or LatAm buyers: "Dear Mr./Ms. [Surname]" or "Estimado/a Sr./Sra. [Apellido]". Use a first name
   only if they signed with one. [Biz Latin Hub][c1]
2. **Mirror their request in their own terms**, including sites, operating hours, hazard, referral and budget timing. They'll agree
   with this line because it's what they told us. [Berman, Entrepreneur][b5], [Godin, customer isn't trying to save money][g7]
3. **Outcome for them**, in one or two sentences tied to their stated goal. [Lopuch, Predictable Revenue][l4]
4. **One proof point**, the single most relevant verified deployment from Stage 4, or what the sources say FlytBase did with
   the referrer. It must have an S# source, and one strong case study beats a capability list. [Berman, 3Cs][b6], [Berman templates][b3]
5. **Optional one-line preview** of how a pilot or rollout would start. [Lopuch, Predictable Revenue][l4]
6. **At most 2 discovery questions**, each mapped to a Stage 1 gap. [gked2121 inbound-lead-qualifier][k1], [marketingskills][m1]
7. **One CTA**: a short call (20-30 min) with **two specific time options in the buyer's time zone**, plus an offer to bring
   their safety or IT colleague and a booking link as fallback only. Write as if the reply is expected ("Would Tuesday 10:00 or
   Wednesday 15:00 Santiago time work?"). [Lopuch, Woodpecker][l2], [Berman templates][b3], [marketingskills reply-handling][m2]
8. **Language offer** for buyers in Spanish-speaking countries: "Con gusto podemos continuar en español." [Biz Latin Hub][c1]
9. **Signature** with full name, role, company and direct contact, never "FlytBase Team". [Godin, Email checklist][g8], [Lopuch][l2]

**Length.** It should fit on one phone screen, about 120-180 words of content. **[py]** The whole body is at most 200 words.
[Berman, How to cold email][b1], [Factmata pattern via AngelBacked][d1]

**Questions.** **[py]** Email 1 has at most 3 question marks (2 discovery questions plus the CTA). [gked2121][k1]

**Subject.** Reply in their original thread with a real `Re:`. If a new thread is needed, use a plain subject that describes the content and
names their company or sites and the use case, e.g. "SQM lithium sites: drone operations next steps". No clever hook, no
Title Case hype, no emoji, no "!". **[py]** The subject has at most 8 words and no "!" or emoji, and never a fake `Fwd:`.
[Berman, subject lines][b2], [Godin, Email checklist][g8], [Lopuch, Agents of Change][l5]

**Tone by seniority, industry and region.** [marketingskills cold-email][m1], [Commisceo Chile][c2]
- C-suite or Head of: brief, peer-level and understated, leading with outcomes and safety. Technical readers: precise, with specs linked rather than pasted.
- Mining: safety of crews, uptime, remote sites, permits. Spell out acronyms and use no jargon. [Lopuch][l4]
- Chile: formal "usted", titles and surnames, diplomatic tone, no pressure for a quick close. Name a trusted introduction (the referral) early.
  Times go in `America/Santiago` (CLST, UTC-3, until April 2027). Don't hard-code an offset. [timeanddate][c3]

## 3. Follow-up sequence (the buyer went quiet)

**4 emails in the active sequence: Email 1 plus 3 follow-ups.** Berman uses 4 touchpoints, and Lopuch caps it at 5 emails. Three follow-ups is the
conservative count for an enterprise inbound buyer. [Berman, follow-ups][b4], [Lopuch, Copy Hackers][l1]

| Step | When (buyer's business days) | What it adds | Ask |
|---|---|---|---|
| 1 | Day 0, same business hour | Mirror, outcome, one proof, max 2 questions | Call with 2 time slots |
| 2 | +2 business days, same thread | One new useful item answering a *different* Stage 1 gap (insight, resource, direct answer) | Same CTA, restated |
| 3 | about +7 | Different angle: peer case study (Stage 4) or a regulatory or safety point. Offer a forwardable summary for colleagues | Smaller yes/no ("Is a short call next week still useful?") |
| 4 | about +12-14 | **Close the loop**: no guilt, offer to hold until their stated timeline or to talk to the right colleague | "Should I check back before your Q3 budget review?" |

Rules:
- Send **Tuesday to Thursday, 10:00-14:00 local time**, and avoid Monday mornings and Friday afternoons. [Berman][b4], [Lopuch][l1]
- **Same thread, same subject**, so their own request stays visible. [Berman][b4], [Lopuch, Agents of Change][l5]
- **Each touch adds one new thing** the buyer would miss if it didn't come. A reminder that we exist isn't enough. [Godin, Four steps][g9], [Godin][g1]
- **One ask per email, and at most one link** with no homework. If they go quiet, make the next ask *smaller*. [Lopuch, AMI][l3], [marketingskills emails][m4]
- **[py]** Every follow-up is **shorter than Email 1**, about 2-4 sentences and under 120 words. [Berman][b4], [Lopuch][l5]
- Each email makes sense on its own. [marketingskills cold-email][m1]
- **[py]** The last email is a **close-the-loop** email that leaves the door open. [Berman, breakup][b4], [louisblythe ghost-recovery][o1]
- **After the sequence**, the lead is a *ghost*, not a dead lead. Move it to value nurture every 4-6 weeks, or one refreshed touch tied to
  their stated trigger (Q3 budget). Nurture order: case study, then implementation approach, then objections (permits, security, integration),
  then a scoped pilot. [Berman, TAM recycle][b7], [marketingskills sequence templates][m5]
- **Keep every promise.** "I'll send X by Thursday" becomes a CRM task. [Godin][g1]

## 4. Multi-stakeholder enterprise adaptation

- Enterprise purchases are decided by a group: site managers, HSE, IT/OT security, procurement and finance. Act as a buying coach for
  your champion. [CEB, Making the Consensus Sale][e1]
- By touch 2 or 3, offer to include their safety or IT colleagues, and give a **5-bullet forwardable summary** (problem, approach, safety and
  compliance, integration and IT, proposed pilot and next step) they can paste internally. [CEB][e1]
- For budget timing, offer to help build the business case (an ROI brief or pilot scope for finance) and agree a date. Don't push.
  [marketingskills objection library][m7]
- Record the referrer. The handoff prompts the account owner to thank and update them, if the BDR approves. [TheCraigHewitt referral-intro][h1]
- After any call, send a written recap the same day with next steps, owners and dates. [louisblythe follow-up-discipline][o2], [Commisceo][c2]

## 5. Reply branches (any reply pauses the sequence)

Classify every reply, and draft each response for the BDR to send. Nothing is sent automatically. [marketingskills reply-handling][m2]

| Reply | Action |
|---|---|
| Positive | Answer within the business hour. Offer 2 specific times and a link. No essay. [Berman templates][b3] |
| "Send info" / "how much?" | Offer a short call to tailor it to their sites. Price depends on sites, docks and integrations. No price sheet before a call. [Berman][b3] |
| Not now / Q3 budget | Thank them, offer one small step (pilot scope or a business-case brief), log the date and stop until then. [marketingskills objections][m7] |
| Referral to a colleague | Thank them, write to the named person mentioning who referred us, and copy the buyer only if that's appropriate. [m2] |
| Objection (security, permits, vendor) | Why they raise it, then approach, proof point and one follow-up question. [m7] |
| Out of office | Pause until the day after they return, and note any stand-in. [Berman][b4] |
| Polite non-commitment (Chile: "lo vamos a ver") | Log it as not-yet, not as interest. Confirm next steps in writing. [Biz Latin Hub][c1] |
| No / unsubscribe / hostile | Stop on every channel immediately. Don't argue. [Godin][g1], [m2] |

## 6. Never do

**[py]** These phrases are banned in the subject and body. Python lints for them.
- Cold-email openers: "I hope this email finds you well", "My name is", "I came across", "I'm reaching out", "sorry to bother".
- Empty follow-ups: "just checking in", "circling back", "bumping this", "did you see my last email", "I never heard back",
  "I know you're busy", "quick question", "hope to hear back", "feel free to reach out", "touching base".
- Buzzwords and hype: leverage, synergy, best-in-class, seamless, robust, unlock, game-changer, cutting-edge, revolutionary, world-class,
  "act now", "limited time".
- AI tells: "it's not X, it's Y" contrast reveals, em dashes in short copy, self-answered questions, tidy quotable closers. [marketingskills ai-tells][m3]
- **[py]** No template placeholders (`{first_name}`, `[Company]`, `[NEED: ...]`) in a body. Gaps go in BDR notes as `[NEED: ...]`. [Godin, Ouch][g2], [m3]

Also never:
- Invent facts, customers, quotes, statistics, site details or a referrer relationship. Every buyer fact needs an S# source. [m3]
- Dump features or specs, or lead with price or discounts. [Berman][b3], [Godin][g7]
- Ask for a long demo, a contract or a pilot in Email 1, or put several asks in one email. [Lopuch][l2], [Factmata pattern][d1]
- Use fake urgency, countdowns, emoji or ALL CAPS. [Berman, subject lines][b2]
- Use first names, "tú" or a casual tone with a senior Chilean executive in early emails. [c1]
- Add the contact to marketing lists, or copy cold-email deliverability tactics (warmup, secondary domains, open tracking). [Godin][g1], [m1]
- Send or draft in Gmail. Drafts go to the BDR through the Lead Desk only (project rule).

## 7. Pre-save checklist (the writer self-checks and records it in `playbook_checks`)

1. Email 1 mirrors the buyer's exact request and names the referral and timeline they gave.
2. Email 1 has one proof point with an S# source and no feature list.
3. Email 1 has at most 2 discovery questions, each mapped to a Stage 1 gap. **[py]**
4. Email 1 has one CTA with two specific times in the buyer's time zone. **[py]**
5. Email 1 is at most 200 words, and every follow-up is shorter than Email 1. **[py]**
6. Each follow-up adds one new item, targets a different gap and has one ask and at most one link. **[py, links]**
7. The last email closes the loop and offers to hold until their stated timeline. **[py]**
8. There are no banned phrases, buzzwords, placeholders, em dashes or fake `Fwd:`. **[py]**
9. "You/your" outnumbers "we/our" in Email 1, and at most 2 sentences start with "I" or "We". **[py, you vs we]** [Lopuch, Woodpecker][l2]
10. The subject describes the content in 8 words or fewer, in sentence case, with no "!". **[py]**
11. Each email is signed by the named BDR with contact details. **[py]**
12. Read it aloud and ask "could it be shorter?" Reread every sentence over 20 words. [Godin, Email checklist][g8], [m3]

## Sources

[g1]: https://seths.blog/2008/01/permission-mark/
[g2]: https://seths.blog/2008/04/ouch/
[g3]: https://seths.blog/2012/06/seven-marketing-sins/
[g4]: https://seths.blog/2014/04/deconstructing-generosity/
[g5]: https://levels.com/podcasts/building-community-tribalism-and-the-principle-of-people-like-us-do-things-like-this-seth-godin-ben-grynol
[g6]: https://seths.blog/2019/03/the-minimum-viable-audience-2
[g7]: https://seths.blog/2017/02/maybe-your-customer-isnt-trying-to-save-money/
[g8]: https://seths.blog/2008/06/email-checklist/
[g9]: https://seths.blog/2016/08/marketing-in-four-steps/
[b1]: https://alexberman.com/how-to-cold-email
[b2]: https://alexberman.com/good-cold-email-subject-lines
[b3]: https://alexberman.com/cold-email-templates
[b4]: https://alexberman.com/cold-email-follow-up
[b5]: https://entrepreneur.com/growing-a-business/how-to-write-cold-emails-that-get-opens-and-get-sales/316605
[b6]: https://devrims.com/blog/?p=52532
[b7]: https://alexberman.com/cold-email-tam-strategy-skip-followups-breakdown
[l1]: https://copyhackers.com/how-to-write-cold-emails/
[l2]: https://woodpecker.co/blog/bad-cold-email-to-good-cold-email-examples/
[l3]: https://agencymanagementinstitute.com/?p=24577
[l4]: https://predictablerevenue.com/blog/writing-emails-work-conversation-copywriting-specialist-laura-lopuch/
[l5]: https://www.theagentsofchange.com/laura-lopuch
[d1]: https://www.angelbacked.co/blog/cold-emails-that-got-founders-funded (Dhruv Ghulati / Factmata, third-party account; exact email text unverified)
[m1]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/cold-email/SKILL.md
[m2]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/cold-email/references/reply-handling.md
[m3]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/copywriting/references/ai-tells.md
[m4]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/emails/SKILL.md
[m5]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/emails/references/sequence-templates.md
[m6]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/revops/references/routing-rules.md
[m7]: https://github.com/coreyhaines31/marketingskills/blob/main/skills/sales-enablement/references/objection-library.md
[k1]: https://github.com/gked2121/claude-skills/blob/main/inbound-lead-qualifier/SKILL.md
[o1]: https://github.com/louisblythe/Sales-Skills/blob/main/skills/follow-up-discipline/SKILL.md (and ghost-recovery-sequences)
[o2]: https://github.com/louisblythe/Sales-Skills/blob/main/skills/follow-up-discipline/SKILL.md
[h1]: https://github.com/TheCraigHewitt/skills/blob/main/sales/referral-intro/SKILL.md
[e1]: https://www.oreilly.com/library/view/hbrs-10-must/9781633699366/10147/OEBPS/xhtml/chapter008.xhtml (CEB; group size figures not verified, principle only)
[y1]: https://www.yesware.com/blog/fast-is-only-the-first-step/
[s1]: https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf
[c1]: https://www.bizlatinhub.com/chile-business-etiquette/
[c2]: https://www.commisceo-global.com/country-guides/chile-guide
[c3]: https://www.timeanddate.com/time/change/chile/santiago
