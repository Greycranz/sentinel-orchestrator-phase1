@echo off
setlocal

REM Try PowerShell 7+ first, fall back to 5.1
where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0secrets.ps1" %*
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0secrets.ps1" %*
)
