@echo off
echo Installing the robot tools (one time only)...
where py >nul 2>nul && (py -m pip install -r requirements.txt) || (python -m pip install -r requirements.txt)
echo.
echo Done! Now double-click run.bat
pause
