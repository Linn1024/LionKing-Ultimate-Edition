@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0scripts\Setup.ps1" %*
if errorlevel 1 pause
