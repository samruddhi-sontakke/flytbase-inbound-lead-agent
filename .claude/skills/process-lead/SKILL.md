---
name: process-lead
description: Queue one inbound email (a file path, or pasted text) as a Lead Desk lead and run the six stages on it right away, without sweeping Gmail. Usage /process-lead input/lead_sqm.txt
---

1. If the argument is a file path, run `py run.py --input <path>` (it queues the file as a lead with source "cli").
   If it's pasted email text, save it to a temporary file in the scratchpad and queue that file.
2. Follow section 3 ("Run the queue") of `.claude/skills/process-inbox/SKILL.md` for that lead, then section 4.
   Skip the Gmail sweep.
