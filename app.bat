@echo off
REM Internal Inbound Lead Desk - opens http://127.0.0.1:8000 (this machine only)
start "" http://127.0.0.1:8000
where py >nul 2>nul && (py -m app.server) || (python -m app.server)
pause
