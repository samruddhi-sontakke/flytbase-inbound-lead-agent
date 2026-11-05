"""Inbound Lead Agent - run the full six-stage pipeline on one inbound email.

Usage:
    python run.py                          # uses input/lead_sqm.txt
    python run.py --input input/other.txt  # any other inbound email

Pipeline order (Stage 3 runs after 4 and 5 so the emails can use the case study and partner):
    0 Intake -> 1 Qualify -> 2 Research -> 4 Case study -> 5 Partner -> 3 Emails -> 6 AE handoff

The stages themselves live in agent/pipeline.py, which the web app (app/server.py) also uses.
"""
import argparse
import sys
from pathlib import Path

from agent import config, pipeline


def main():
    ap = argparse.ArgumentParser(description="Inbound lead qualification agent")
    ap.add_argument("--input", default=str(config.ROOT / "input" / "lead_sqm.txt"))
    args = ap.parse_args()

    missing = config.check_keys()
    if missing:
        print(f"\nMissing API key(s): {', '.join(missing)}.\n"
              f"Create a file called .env (or keys.txt) in {config.ROOT} with:\n  GEMINI=your-gemini-key\n  TAVILY=your-tavily-key\n")
        sys.exit(1)

    email_text = Path(args.input).read_text(encoding="utf-8")
    run_dir = pipeline.new_run_dir()

    print("\nINBOUND LEAD AGENT")
    print(f"Input: {args.input}\nOutput folder: {run_dir}\n")
    print(email_text)

    result, sources = pipeline.run(email_text, run_dir, input_file=args.input)
    meta = result["meta"]
    print(f"\n{'=' * 64}\n  DONE in {meta['seconds']}s | {meta['llm_calls']} AI calls | {len(sources.items)} sources")
    print(f"  Report: {run_dir / 'REPORT.html'}\n{'=' * 64}\n")
    return run_dir


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\nSTOPPED: {e}\n")
        sys.exit(1)
