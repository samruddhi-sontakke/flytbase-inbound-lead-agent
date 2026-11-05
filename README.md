# Inbound Lead Agent - FlytBase BDR Assignment

An AI agent workflow that takes **one raw inbound email** and automatically produces everything an
inbound BDR would: MEDDPICC qualification, cited account research, case-study match, partner / GTM
recommendation, an adaptive email sequence and an AE handoff.

Built in Python so that every step is plain, readable code: no black boxes.

## Live run output

**[Read the full six-stage report from the live run](outputs/run_2026-11-05_16-34-35/REPORT.md)**
(184 seconds, 9 AI calls, 57 sources). The raw output of each stage, every source and every AI prompt and
response for that run are in [`outputs/run_2026-11-05_16-34-35/`](outputs/run_2026-11-05_16-34-35/).

What the system found on its own (nothing hard-coded):
- **SQM is already a FlytBase customer.** It has a published case study with Chilean integrator Adentu, so this
  lead is an expansion opportunity, not a cold one.
- **The Anglo American referral connects to a FlytBase case study** (an autonomous mining deployment in Peru).
- **Recommended motion:** AE-led co-sell with Adentu (already deployed at SQM), with Dronestore Chile as backup.
- **A likely internal champion** is named on FlytBase's site (SQM's Deputy Manager of Digital Innovation).

## How it works

```mermaid
flowchart LR
    A[Inbound email] --> S0[0 Intake<br/>extract fields]
    S0 --> S1[1 Qualify<br/>MEDDPICC + scoring]
    S0 --> S2[2 Research<br/>plan - search - write - fact-check]
    S0 --> S4[4 Case study<br/>crawl flytbase.com sitemap]
    S1 --> S5
    S4 --> S5[5 Partner / GTM<br/>partner directory + search]
    S1 & S2 & S4 & S5 --> S3[3 Email sequence<br/>gap-driven, branching]
    S3 --> S6[6 AE handoff]
    S6 --> R[REPORT.html + JSON per stage + trace.jsonl]
```

| Stage | What it does | Tools |
|---|---|---|
| 0 Intake | Turns the free-text email into structured fields (contact, company, sites, pains, referrer). Every later stage reads from this, so **nothing about the lead is hard-coded.** | Gemini |
| 1 Qualification | MEDDPICC: known / partial / unknown for all 8 elements, the missing info, and a discovery question for each gap. The AI rates 7 ICP fit factors 0-5 **with evidence**; the **score itself is calculated in Python** (`s1_qualify.py`), so it's transparent and repeatable. | Gemini + Python |
| 2 Research | The AI **plans** ~12 searches across 6 categories (org structure, capex/opex, news, investor letters, operations, tech adoption), Tavily runs them, the AI writes a brief that must cite source IDs `[S#]`, then a **separate fact-check pass** compares every claim to the text it cites. Unsupported claims are removed and listed. | Tavily + Gemini |
| 4 Case study | Reads FlytBase's **sitemap** to find every case study, downloads all of them, pre-scores them in Python (keyword overlap, plus flags for *mentions the referrer* and *mentions the lead's own company*), then the AI ranks the shortlist. | requests + BeautifulSoup + Gemini |
| 5 Partner / GTM | Reads the FlytBase **partner directory**, searches for partners in the lead's country/region, pulls in partners named in relevant case studies, then decides direct vs partner-led. Python then **checks that every recommended partner name actually appears in a source.** | requests + Tavily + Gemini |
| 3 Emails | Runs after 2, 4 and 5 so the emails use real research, the matched case study and the partner. Each email is mapped to the MEDDPICC gaps it targets, with branches for different replies. | Gemini |
| 6 AE handoff | A 2-minute summary: buyer context, qualification status, top 3 cited findings, case study, GTM motion, next step. | Gemini |

## Design decisions

- **The AI reads, Python decides.** Scores, flags, source registry, fact-check removal and partner verification are deterministic code. The AI is used for reading and writing.
- **No fabricated research.** Each source gets an ID. The writer may only cite IDs, and a second model call checks each claim against the cited text. Anything unsupported is removed and logged in the report.
- **Stage order is 0-1-2-4-5-3-6.** The emails are written last so they can use the case study and partner findings.
- **Everything is inspectable.** Each run saves one JSON file per stage, `sources.json`, and `trace.jsonl` with every prompt and response.
- **Works for any inbound lead.** Put another email in `input/` and run `python run.py --input input/that_file.txt`.

## Run it

1. Install Python 3.10+.
2. Create `keys.txt` in this folder (it is git-ignored):
   ```
   GEMINI=your-gemini-api-key      # free at aistudio.google.com
   TAVILY=your-tavily-api-key      # free at tavily.com
   ```
3. Install and run:
   ```
   pip install -r requirements.txt
   python run.py
   ```
   On Windows you can double-click `setup.bat` once, then `run.bat`.

   Optional: add `GEMINI_MODEL=gemini-flash-lite-latest` (or any other Gemini model) to `keys.txt` to pick
   the model. If a model is busy or over its free-tier limit, the system switches to the next one automatically.

A run takes about 2-5 minutes on the free tiers. Results go to `outputs/run_<date-time>/`:

| File | Contents |
|---|---|
| `REPORT.html` / `REPORT.md` | Full six-stage report with clickable sources |
| `0_lead.json` ... `6_handoff.json` | Raw output of each stage |
| `sources.json` | Every source used, with URL and the query that found it |
| `trace.jsonl` | Every AI prompt and response (full audit trail) |

## Internal web app: Inbound Lead Desk

An internal-only web app over the same pipeline. Each inbound email becomes a lead stored in MongoDB.

- **Leads:** a list with P1/P2/P3 filters, search, and status (New → Working → Meeting booked → Handed to AE).
- **New lead:** paste an email and run the agent. The page shows live progress stage by stage, with the log the command line prints.
- **Lead page:** one tab per stage (AE handoff, MEDDPICC, cited research, emails with copy buttons, case-study ranking, partner), plus sources, the full AI trace, notes, an owner field, and the original email.
- **Ctrl K** jumps to any page or lead.

Setup: add a MongoDB connection string to `.env` next to the API keys:

```
GEMINI=...
TAVILY=...
MONGODB=mongodb+srv://user:pass@cluster.mongodb.net/   # database defaults to flytbase_leads
```

Run it with `py -m app.server` (or double-click `app.bat`), then open http://127.0.0.1:8000. It binds to this machine only.
Earlier command-line runs in `outputs/` are imported automatically. API docs are at `/api/docs`.

## Project layout

```
run.py                    orchestrator: runs the stages in order, saves outputs
input/lead_sqm.txt        the inbound email (the only input)
agent/config.py           keys, model fallback list, research limits
agent/llm.py              Gemini wrapper: retries, model fallback, trace logging
agent/tools.py            web search (Tavily), page reading, sitemap crawler
agent/sources.py          source registry ([S#] IDs)
agent/stages/s0..s6       one file per stage, prompts included
agent/report.py           JSON -> REPORT.md / REPORT.html (no AI)
agent/pipeline.py         the stages as one function, shared by run.py and the web app
app/server.py             web app: FastAPI API + background worker
app/db.py                 MongoDB connection (one document per lead)
app/static/               the UI (plain HTML/CSS/JS, no build step)
```

## Known limitations / next steps

- Public web search can't reach paywalled filings or LinkedIn org charts, so reporting lines are partly inferred (clearly labelled as such).
- The fact-checker is itself a model call. A stricter version would also match numbers and dates to the source text in Python.
- Free-tier rate limits make runs slower than a paid setup would be.
- Next: trigger it from the real contact form (webhook), write the results to the CRM, and send email 1 for human approval in Slack.
