# Walkthrough video script (synced to the PDF)

Open `docs/Inbound-Lead-Desk-Walkthrough.pdf` (or the interactive deck) full-screen. Each section below is one PDF page: say the text, and where a **Show** list appears, switch to the live system, do those steps, then come back to the next page. Target length: about 10.5 minutes (the brief asks for 8–12).

The five topics the brief requires are tagged: **[architecture]** p3–4, **[live run]** p5–11, **[framework choice]** p6, **[design decision]** p13, **[limitation]** p14.

## Before you record

- Lead Desk running: `py -m app.server` → http://127.0.0.1:8000, with the SQM lead open in a tab.
- Claude Code open in the project folder with the `leaddesk` MCP connected (`/mcp`), the cron set up (`/process-inbox` every 5 min).
- Gmail open in another tab. Have one test email from `input/TEST_CASES.md` ready to send from samruddhisontkke@gmail.com.
- Optional: the repo open on GitHub to show the run folder.

## PDF page 1 · Inbound Lead Desk
*0:00 – 0:40*

Hi, I'm Samruddhi, and in this video I'll walk you through the inbound lead system I built for the FlytBase BDR assignment. The brief asked for a system, not a document: something that takes a raw inbound email and does what an inbound BDR does. So instead of reading an email, researching the company, finding a case study, drafting replies and deciding who should handle the lead by hand, I built an agent that does all of it, stores the results and shows them on an internal Lead Desk. I'll show the architecture, run it live on the assigned lead, Rodrigo Castillo from SQM, walk through all six stages, and finish with a design decision I'm proud of and what I'd improve.

## PDF page 2 · One raw inbound email in. Six BDR artifacts out, written by a system.
*0:40 – 1:10*

The assignment asks for six stages: qualification, deep account research, response generation, case-study matching, partner identification and an AE handoff, all from one raw inbound email. The core rule is "you're not writing the answers, you're building the thing that writes the answers". So nothing you'll see was written by hand. And because the PDF lists exact requirements for each stage, I turned every bullet into a check in Python. Each stage's output is tested against the PDF before it's saved, and you'll see a PDF checklist on every stage in the app.

## PDF page 3 · How the pieces connect
*1:10 – 2:10* · **[architecture]**

Here's the architecture. Claude Code is the AI agent. It's connected to Gmail through an email MCP, which can read and label mail. Sending, replying and drafting are blocked in its settings. A cron runs every five minutes, so the agent checks the inbox on its own rather than me triggering it. Claude Code is the orchestrator: it decides what to run and hands each stage to its own subagent. There are seven, one per PDF stage plus an independent fact-checker, and each one is a versioned file with its own instructions and output format, so the logic is inspectable. Everything that has to be exact lives in a Python MCP server I wrote, called leaddesk: the scoring, the source registry, the website crawls, removing unsupported claims, checking partner names and checking every stage against the PDF. Results go into MongoDB, and the Lead Desk web app shows them. So this isn't one prompt producing a report. It's a multi-stage workflow with separate responsibilities, stored outputs and validation.

## PDF page 4 · Dependency-aware, not one long chain
*2:10 – 2:50* · **[architecture]**

This is one tick of the agent. First it sweeps every unread email. Python scores each one for contact-form markers, and the agent decides whether it's a lead and writes down why. Then the stages run in dependency order. Stage 1 first. Research and case-study matching both need only Stage 1, so they run in parallel. The fact-checker runs on the research. Emails and partner identification run next, then the handoff. I did this on purpose: making every stage wait for the one before would only slow it down. Every stage saves through Python, which validates it, computes scores, checks it against the PDF, and stores it in MongoDB and in a run folder. There's a lock so only one lead runs at a time, and every subagent call is written to a trace.

## PDF page 5 · The lead arrives in Gmail
*2:50 – 3:50* · **[live run]**

Switch to Gmail. Here's the input: an email to my inbox in the flytbase.com contact-form format. Rodrigo Castillo, Head of Operations, Northern Operations Division at SQM, wants drone inspection for three large 24/7 lithium sites in the Atacama. Contracted crews are expensive and hazardous, he was referred by Anglo American, and a budget conversation is set for Q3. Now switch to the Claude Code session and type /process-inbox, or wait for the five-minute cron. The agent reads every unread email. On its first run it checked 54, mostly job alerts. Python scores each one for contact-form signals, and the agent makes the call and records a reason. Open the Inbox page: this was the only lead, with a marker score of 12, and everything else is marked not a lead. Back in Gmail, the thread now has LeadDesk/Seen and LeadDesk/Lead labels, and it's still unread, because the agent never marks mail read and never replies. Then open the lead: the live log shows Stage 1 starting, and then research and case study running in parallel. A full run takes about 15 to 17 minutes, so I'll walk through the finished run next.

**Show:**

- Switch to **Gmail** (sontakkesamruddhijain89@gmail.com): show the SQM email and its labels.
- Switch to **Claude Code**: type `/process-inbox` (or let the 5-minute cron fire) and show it sweeping the inbox.
- Switch to the **Lead Desk** (http://127.0.0.1:8000) › **Inbox**: the verdicts and the marker score of 12.
- Back in **Gmail**: the `LeadDesk/Seen` + `LeadDesk/Lead` labels, still unread.
- Open the lead: the live log shows Stage 1, then research and case study running in parallel.
- Tip: send a fresh test from `input/TEST_CASES.md` (e.g. #2 or #5) a minute before this page so something new is picked up live.

## PDF page 6 · MEDDPICC, scored in Python
*3:50 – 4:40* · **[framework choice · live run]**

Stage 1 is qualification. I chose MEDDPICC because this is an enterprise B2B deal: several large sites, a buying committee with operations, safety, IT and procurement, and very likely a local partner. BANT is too shallow for that, and SPICED fits recurring SaaS expansion better. MEDDPICC also makes the gaps explicit, and the gaps are what the emails go after. The agent extracts what the email tells us and marks each element known, partial or unknown. Pain is known. The economic buyer, metrics, decision process, champion and competition are only partial, and decision criteria and paper process are unknown. It doesn't assume what isn't there. Then the AI rates seven ICP fit factors, each with evidence, and Python does the math: ICP fit 91, MEDDPICC completeness 44 percent, priority 77, so P1 hot. You can see the calculation line by line. A high-fit lead isn't the same as a qualified opportunity, and the score shows both.

**Show:**

- Lead Desk › SQM lead › **01 Qualification**: the scores, the Python calculation, the MEDDPICC rows (click one to show its discovery question).

## PDF page 7 · Real sources, then an independent fact-check
*4:40 – 5:30* · **[live run]**

Stage 2 is deep account research. The agent plans 16 searches across the PDF's categories: org structure and reporting lines, budget signals from filings, recent news, investor letters and operations. It uses web search, reads each page, and checks Reddit for practitioner context. Every page is stored with its raw text and gets an ID like S7, and the brief may only cite those IDs. Then a separate fact-checking agent, which didn't write the research, checks every claim against the stored text. For SQM that was 33 sources and 43 claims: 41 supported, 2 partial, none removed. Anything unsupported would be cut and listed, never shown as fact. The finding I'd point an AE to: since December 2025, SQM's Atacama lithium operations run under Novandino, a joint venture with Codelco, so the contracting entity may not be SQM itself. The output isn't a company overview. It's why SQM might need FlytBase and how to position it.

**Show:**

- **02 Research**: the positioning, a cited claim (click an S# chip to open its source), and the fact-check note under a finding.

## PDF page 8 · SQM is already a FlytBase customer
*5:30 – 6:15* · **[live run]**

Stage 4 is case-study matching. The agent crawls FlytBase's sitemap and reads all 24 case studies. Python pre-scores each one, and it flags any case study that names the lead's own company or the referrer, using the names from the email rather than anything hard-coded. The biggest finding of the whole run: SQM is already a FlytBase customer. There's a published case study where the Chilean integrator Adentu runs FlytBase docks across a 678 square kilometre SQM operation in the Atacama. So this isn't a cold lead, it's an expansion. The Anglo American referral connects to a different case study, Quellaveco in Peru, deployed with UAV Latam. The system also spotted that the SQM page gives two different yield figures, two percent in the body and four times in the headline, so neither one goes into an email. Stage 5, partner identification, reads the partner directory and searches for LATAM partners. It recommends an AE-led co-sell with Adentu, which already knows SQM's sites and people, with Dronestore Chile as backup. Python checks that every partner name actually appears in a stored source.

**Show:**

- **04 Case study**: the green "Already a FlytBase customer" box and the ranking. Then **05 Partner**: Adentu with "name found in sources".

## PDF page 9 · A reply to an inbound, not a cold email
*6:15 – 7:05* · **[live run]**

Stage 3 writes the reply sequence, and the key point is that this is an inbound reply, not cold outreach. Rodrigo asked us. So I researched how good teams write and follow up, from Seth Godin's permission marketing, Alex Berman, Laura Lopuch and an open marketing-skills library, and turned it into one playbook with a source on every rule. Email 1 goes out the same business hour. It mirrors what he told us: three 24/7 sites, costly and hazardous crews, the Anglo American referral and Q3. It uses one proof point, SQM's own deployment, asks two questions mapped to his MEDDPICC gaps, and offers two call times in Santiago time, with an offer to continue in Spanish. Each follow-up targets a different gap, adds something new and gets shorter, and the last one closes the loop politely. Python checks the measurable rules: length, question count, time slots, banned phrases and signature. The first draft of email 1 was 212 words, so it was rejected and the agent cut it to 192. These are drafts: nothing is sent automatically.

**Show:**

- **03 Emails**: read the opening of email 1, show the tone adaptation panel and the PDF + playbook checklist at the bottom.

## PDF page 10 · The AE knows exactly what to do next
*7:05 – 7:45* · **[live run]**

The last stage is the AE handoff, where everything comes together. It covers who Rodrigo is, what he cares about and who else is involved; the qualification status with knowns and unknowns; the top three research findings, each cited; the recommended case study; the go-to-market motion; and a concrete next step. Here it is: send email 1 today, then a 30-minute discovery call on Tuesday the 10th or Wednesday the 11th, Santiago time. Before that, check internally who owns the SQM account and confirm Adentu is still a partner. On the call, confirm whether he sits in SQM or Novandino, which three sites and which Q3 he means, and who owns the budget, then close on a one-site pilot with Adentu. The AE doesn't need to reread the email or redo the research.

**Show:**

- **06 AE handoff**: the suggested next step box, buyer context and top 3 findings.

## PDF page 11 · Every claim, check and call is inspectable
*7:45 – 8:30* · **[live run]**

Back on the lead page. Every stage tab ends with its PDF checklist, the requirements from the assignment checked in Python. This lead passes all 39, including the playbook checks on the emails. The Sources tab lists all 33 sources, each with its link, and every citation in the research is clickable. The Agent trace tab shows each subagent call: which agent file ran, what it was given and exactly what it saved. Then open the report, REPORT.html. The same thing is in the repo as REPORT.pdf, plus one JSON file per stage. That's the live run output for the submission. Nothing here is a black box.

**Show:**

- Scroll to a tab's **assignment PDF checklist**, open **Sources**, open **Agent trace** (expand one entry), click **Report**.
- Optional: open the repo folder `outputs/run_2026-11-05_19-32-11/` to show REPORT.pdf and the stage JSON files.

## PDF page 12 · A second lead, a different answer
*8:30 – 9:00*

To show this isn't tuned to one email, I sent a second test lead: a Head of Asset Inspection at E.ON in Germany, asking about docked drones for about 40 substations. Same code, a different answer. It came out P2 warm, one point under P1 because there was no referral, and the score says so honestly. Research found the likely buyer is Bayernwerk Netz. The case study is EnBW, and the system says plainly that EnBW's assets are solar farms, not substations. The partner is Droniq, because of BVLOS approval in Germany. The emails use CET times and offer German instead of Spanish. And the fact-checker removed six claims whose source turned out to be unreadable, instead of letting them through.

**Show:**

- Optional: open the E.ON lead in the Lead Desk (P2 warm) to show it live.

## PDF page 13 · The AI reads and writes. Python decides.
*9:00 – 9:45* · **[design decision]**

The design decision I'm proudest of is the split between the AI and the code. The AI reads, judges and writes. Python decides anything that has to be exact: the scores, which facts survive, whether a partner name is real, and whether each stage meets the PDF. That's also why the orchestration is dependency-aware and every stage saves through the same validated path. It matters because it fails safe. On the first SQM run, the fact-checker was only shown the first part of each source, so it removed 16 claims that were actually true. Nothing false got through, but real research was lost. I found it, fixed the tool so it passes the relevant passages and the full text, re-ran the check, and none were removed. On the E.ON lead, a Word file was stored as unreadable data, and the checker cut every claim that rested on it rather than trusting it. Nothing unsourced reaches the AE.

## PDF page 14 · What I’d improve with more time
*9:45 – 10:20* · **[limitation]**

Now the limitations, honestly. The biggest: the five-minute cron lives inside the Claude Code session, so it stops when the session closes and expires after seven days. For production I'd run it headless on a real scheduler or trigger it from a Gmail push notification. Second, the judgement steps are still model output. Python bounds them with schemas, citations, verification and checklists, but a human should approve email 1, ideally through Slack. Third, it only uses the public web. Rodrigo and his division don't show up in any public source, and the system flags that rather than guessing; CRM and enrichment data, plus LinkedIn through the browser, would close that gap. And there's no CRM sync yet: results live in MongoDB and the Lead Desk. I'd prioritise those before running this unattended.

## PDF page 15 · More than an email generator: a system that does the BDR’s first hour, every time.
*10:20 – 10:50*

To sum up: I wanted to build more than an AI email generator. This is an inbound system that picks up the lead from the inbox, qualifies it, researches the account with real sources, finds the right case study and partner, writes the replies and hands a clear next step to the AE, with every step stored and checked. Everything is in the GitHub repo: the code, the agent definitions, the live run output with its report, and this deck as a PDF. That's the system I built. Thank you for watching.
