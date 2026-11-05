"""Inbound Lead Agent - run the full six-stage pipeline on one inbound email.

Usage:
    python run.py                          # uses input/lead_sqm.txt
    python run.py --input input/other.txt  # any other inbound email

Pipeline order (Stage 3 runs after 4 and 5 so the emails can use the case study and partner):
    0 Intake -> 1 Qualify -> 2 Research -> 4 Case study -> 5 Partner -> 3 Emails -> 6 AE handoff
"""
import argparse
import datetime
import json
import sys
import time
from pathlib import Path

from agent import config, llm, log, report
from agent.sources import Sources
from agent.stages import s0_parse, s1_qualify, s2_research, s3_emails, s4_case_study, s5_partner, s6_handoff


def main():
    ap = argparse.ArgumentParser(description="Inbound lead qualification agent")
    ap.add_argument("--input", default=str(config.ROOT / "input" / "lead_sqm.txt"))
    args = ap.parse_args()

    missing = config.check_keys()
    if missing:
        print(f"\nMissing API key(s): {', '.join(missing)}.\n"
              f"Create a file called keys.txt in {config.ROOT} with:\n  GEMINI=your-gemini-key\n  TAVILY=your-tavily-key\n")
        sys.exit(1)

    email_text = Path(args.input).read_text(encoding="utf-8")
    started = datetime.datetime.now()
    run_dir = config.OUTPUT_DIR / started.strftime("run_%Y-%m-%d_%H-%M-%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    llm.TRACE_FILE = run_dir / "trace.jsonl"

    print("\nINBOUND LEAD AGENT")
    print(f"Input: {args.input}\nOutput folder: {run_dir}\n")
    print(email_text)
    t0 = time.time()
    sources = Sources()

    lead = s0_parse.run(email_text)
    qual = s1_qualify.run(lead)
    research = s2_research.run(lead, sources)
    case = s4_case_study.run(lead, sources)
    partner = s5_partner.run(lead, qual, case, sources)
    emails = s3_emails.run(lead, qual, research, case, partner)
    handoff = s6_handoff.run(lead, qual, research, case, partner, emails)

    calls = sum(1 for _ in open(llm.TRACE_FILE, encoding="utf-8")) if llm.TRACE_FILE.exists() else 0
    result = {
        "meta": {"started": started.strftime("%Y-%m-%d %H:%M"), "seconds": round(time.time() - t0), "llm_calls": calls,
                 "input_file": args.input},
        "lead": lead, "qualification": qual, "research": research, "case_study": case,
        "partner": partner, "emails": emails, "handoff": handoff,
    }

    # save each stage as its own JSON file so every step can be inspected
    names = ["lead", "qualification", "research", "emails", "case_study", "partner", "handoff"]
    for i, key in enumerate(["lead", "qualification", "research", "emails", "case_study", "partner", "handoff"]):
        (run_dir / f"{i}_{names[i]}.json").write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "sources.json").write_text(json.dumps(sources.public_list(), indent=2, ensure_ascii=False), encoding="utf-8")

    md = report.build(result, sources)
    (run_dir / "REPORT.md").write_text(md, encoding="utf-8")
    (run_dir / "REPORT.html").write_text(report.to_html(md, "Inbound Lead Report"), encoding="utf-8")

    print(f"\n{'=' * 64}\n  DONE in {result['meta']['seconds']}s | {calls} AI calls | {len(sources.items)} sources")
    print(f"  Report: {run_dir / 'REPORT.html'}\n{'=' * 64}\n")
    return run_dir


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\nSTOPPED: {e}\n")
        sys.exit(1)
