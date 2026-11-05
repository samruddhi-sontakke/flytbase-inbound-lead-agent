# Submission: FlytBase BDR (Inbound) assignment

**Samruddhi Sontakke** · [samruddhisontakke.com](https://samruddhisontakke.com/) · [sontakkesamruddhijain89@gmail.com](mailto:sontakkesamruddhijain89@gmail.com) · +91 72196 00321 · [LinkedIn](https://www.linkedin.com/in/samruddhi-sontakke-11601621a)

The assignment asks for three deliverables. Here is each one.

## 1. Working system access
**Repository:** https://github.com/samruddhi-sontakke/flytbase-inbound-lead-agent

The logic can be inspected at every step:

| What | Where |
|---|---|
| Orchestrator (one agent tick: Gmail sweep → queue → stages → finish) | [`.claude/skills/process-inbox/SKILL.md`](.claude/skills/process-inbox/SKILL.md) |
| One agent per stage, with its prompt and output schema | [`.claude/agents/`](.claude/agents/) |
| Inbound reply playbook used by Stage 3 (each rule sourced) | [`.claude/agents/references/inbound-reply-playbook.md`](.claude/agents/references/inbound-reply-playbook.md) |
| Deterministic tools: scoring, sources, crawls, fact-check removal, PDF checklist | [`leaddesk_mcp/server.py`](leaddesk_mcp/server.py), [`agent/store.py`](agent/store.py), [`agent/stages/`](agent/stages/) |
| Lead Desk web app | [`app/`](app/) |
| Tests | [`tests/`](tests/) (`py -m pytest tests`) |

How to run it is in the [README](README.md#run-it).

## 2. Live run output
The assignment's input email (Rodrigo Castillo, SQM) as processed by the system, from Gmail through all six stages:

- **Report:** [REPORT.md](outputs/run_2026-11-05_19-32-11/REPORT.md) · [REPORT.pdf](outputs/run_2026-11-05_19-32-11/REPORT.pdf) · [REPORT.html](outputs/run_2026-11-05_19-32-11/REPORT.html)
- **Raw stage outputs:** `0_lead.json` … `6_handoff.json`, `sources.json` (33 sources) and `trace.jsonl` (every agent call) in [the run folder](outputs/run_2026-11-05_19-32-11/)
- **Result:** P1 hot, priority 77. Assignment and playbook requirements: 39/39 met.

A second lead, a test sent to show the system generalises: [E.ON run](outputs/run_2026-11-05_20-03-27/REPORT.md) (P2 warm, 29/29).

## 3. Walkthrough video (8–12 minutes)
- **Video:** _[add the Loom / YouTube unlisted link here]_
- **Slides shown in the video:** [docs/Inbound-Lead-Desk-Walkthrough.pdf](docs/Inbound-Lead-Desk-Walkthrough.pdf)
- **Script, synced to the slides page by page:** [docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md)

It covers the architecture (pages 3–4), a live run (pages 5–11), the framework choice (page 6), a design decision (page 13) and a limitation (page 14).
