@echo off
REM Queue input\lead_sqm.txt (or another file) as a lead for the Claude Code agent
where py >nul 2>nul && (py run.py %*) || (python run.py %*)
pause
