"""The six-stage pipeline as one function, shared by the command line (run.py) and the web app.

Order (Stage 3 runs after 4 and 5 so the emails can use the case study and partner):
    0 Intake -> 1 Qualify -> 2 Research -> 4 Case study -> 5 Partner -> 3 Emails -> 6 AE handoff
"""
import datetime
import json
import time
from pathlib import Path

from . import config, llm, log, report
from .sources import Sources
from .stages import s0_parse, s1_qualify, s2_research, s3_emails, s4_case_study, s5_partner, s6_handoff

STAGE_FILES = [("lead", "0_lead"), ("qualification", "1_qualification"), ("research", "2_research"),
               ("emails", "3_emails"), ("case_study", "4_case_study"), ("partner", "5_partner"),
               ("handoff", "6_handoff")]


def new_run_dir(started=None):
    started = started or datetime.datetime.now()
    run_dir = config.OUTPUT_DIR / started.strftime("run_%Y-%m-%d_%H-%M-%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def run(email_text, run_dir, input_file=None, on_stage_done=None):
    """Run all stages on one inbound email. Saves the same files as always and returns
    (result_dict, sources). on_stage_done(key, output) is called after each stage."""
    run_dir = Path(run_dir)
    llm.TRACE_FILE = run_dir / "trace.jsonl"
    llm._dead_models.clear()
    log.reset_clock()
    started = datetime.datetime.now()
    t0 = time.time()
    sources = Sources()

    def done(key, value):
        if on_stage_done:
            on_stage_done(key, value)
        return value

    lead = done("lead", s0_parse.run(email_text))
    qual = done("qualification", s1_qualify.run(lead))
    research = done("research", s2_research.run(lead, sources))
    case = done("case_study", s4_case_study.run(lead, sources))
    partner = done("partner", s5_partner.run(lead, qual, case, sources))
    emails = done("emails", s3_emails.run(lead, qual, research, case, partner))
    handoff = done("handoff", s6_handoff.run(lead, qual, research, case, partner, emails))

    calls = sum(1 for _ in open(llm.TRACE_FILE, encoding="utf-8")) if llm.TRACE_FILE.exists() else 0
    result = {
        "meta": {"started": started.strftime("%Y-%m-%d %H:%M"), "seconds": round(time.time() - t0), "llm_calls": calls,
                 "input_file": input_file or "web app"},
        "lead": lead, "qualification": qual, "research": research, "case_study": case,
        "partner": partner, "emails": emails, "handoff": handoff,
    }

    # save each stage as its own JSON file so every step can be inspected
    for key, name in STAGE_FILES:
        (run_dir / f"{name}.json").write_text(json.dumps(result[key], indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "sources.json").write_text(json.dumps(sources.public_list(), indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "input.txt").write_text(email_text, encoding="utf-8")

    md = report.build(result, sources)
    (run_dir / "REPORT.md").write_text(md, encoding="utf-8")
    (run_dir / "REPORT.html").write_text(report.to_html(md, "Inbound Lead Report"), encoding="utf-8")
    return result, sources
