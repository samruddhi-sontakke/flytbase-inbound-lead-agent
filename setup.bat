@echo off
echo Installing dependencies (one time only)...
where py >nul 2>nul && (py -m pip install -r requirements.txt) || (python -m pip install -r requirements.txt)
echo.
echo Done. Start the web app with app.bat and the agent with Claude Code in this folder.
pause
