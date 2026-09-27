@echo off
rem Stop the Bakery Tracker server, however it was started
rem (visible window, hidden window, or at boot).
rem
rem It finds whichever process is listening on port 3000 and ends just that
rem one, so nothing else on your computer is touched. Your data is unaffected.

setlocal enabledelayedexpansion
set found=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
  set found=1
  echo Stopping the server (process %%p)...
  taskkill /pid %%p /f >nul 2>&1
)
if "%found%"=="0" echo The server is not running.
if "%found%"=="1" echo Done. The server is stopped; your data is untouched.
endlocal
pause
