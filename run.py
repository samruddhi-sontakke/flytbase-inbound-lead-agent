"""Queue an inbound email file as a lead for the agent.

    py run.py                          # queues input/lead_sqm.txt
    py run.py --input input/other.txt  # any other inbound email

The agent is Claude Code: the next /process-inbox tick (session cron) claims the lead and runs the six stages.
To process it right away, type /process-inbox in the Claude Code session. Leads normally arrive by Gmail;
this file path exists for testing and for emails that came in another way.
"""
import argparse
from pathlib import Path

from agent import config, store


def main():
    ap = argparse.ArgumentParser(description="Queue an inbound email for the Lead Desk agent")
    ap.add_argument("--input", default=str(config.ROOT / "input" / "lead_sqm.txt"))
    args = ap.parse_args()
    text = Path(args.input).read_text(encoding="utf-8")
    lead_id = store.create_lead(text, source="cli")
    print(f"Queued lead {lead_id} from {args.input}.")
    print("The agent picks it up on its next tick, or type /process-inbox in Claude Code to run it now.")


if __name__ == "__main__":
    main()
