@echo off
rem ---------------------------------------------------------------------------
rem  Weekly forever-habit: copy the ENTIRE business (database + backups) into
rem  your Google Drive or OneDrive folder, so the bakery survives any device.
rem
rem  Double-click this file once a week. That is the whole ritual.
rem  The folder it creates holds every sale, expense, recipe and customer.
rem ---------------------------------------------------------------------------

set "SRC=%~dp0..\data"
set "DST=%USERPROFILE%\Google Drive\BakeryBackup"

if not exist "%USERPROFILE%\Google Drive" (
  if exist "%USERPROFILE%\OneDrive" set "DST=%USERPROFILE%\OneDrive\BakeryBackup"
)

if not exist "%SRC%" (
  echo Could not find the data folder next to this script.
  pause
  exit /b 1
)

mkdir "%DST%" 2>nul
xcopy "%SRC%" "%DST%\" /E /I /Y /Q >nul

echo.
echo   Backed up to: %DST%
echo   Keep that folder; with it, any computer can become your server again.
echo.
pause
