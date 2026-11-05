# FlytBase BDR (Inbound) assignment: Samruddhi Sontakke

[samruddhisontakke.com](https://samruddhisontakke.com/) · sontakkesamruddhijain89@gmail.com · +91 72196 00321

| # | Item | What it is |
|---|---|---|
| 1 | `1_final-report-SQM.pdf` | The walkthrough deck (15 pages), then the full live run output for the sample lead (SQM) as an appendix |
| 2 | `2_live-run-output-SQM.pdf` | The live run output on its own: the system's report for the assignment's input email |
| 2 | `2_live-run-output-SQM/` | The raw run: one JSON per stage, `sources.json` (38 sources), `trace.jsonl` (every agent call), `input.txt` (the email) |
| 3 | `3_screenshots/` | Real screenshots of the live system: Lead Desk pages for this lead, the inbox sweep, and Gmail labels |

**Links**
- System access (repository): https://github.com/samruddhi-sontakke/flytbase-inbound-lead-agent
- Walkthrough video: https://www.youtube.com/watch?v=vJoj80MXrRc
- This folder in the repository: https://github.com/samruddhi-sontakke/flytbase-inbound-lead-agent/tree/main/submission

**Live run:** the SQM email arrived in Gmail, and the agent picked it up and ran all six stages in one pass: 893 seconds,
P1 hot (priority 73), 39 of 39 assignment and playbook checks met.
