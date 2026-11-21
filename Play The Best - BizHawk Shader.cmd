@echo off
setlocal
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\RunBizHawkShader.ps1" %*
set "TLK_RESULT=%errorlevel%"
if not "%TLK_RESULT%"=="0" pause
exit /b %TLK_RESULT%
