@echo off
where py >nul 2>nul && (py run.py %*) || (python run.py %*)
echo.
echo Opening the report...
for /f "delims=" %%d in ('dir /b /ad /o-n outputs\run_*') do (start "" "outputs\%%d\REPORT.html" & goto :done)
:done
pause
