@echo off
setlocal
if not exist "%~dp0settings\full-genesis" mkdir "%~dp0settings\full-genesis"
if not exist "%~dp0settings\full-genesis\resources.ini" copy /Y "%~dp0profiles\full-genesis.ini" "%~dp0settings\full-genesis\resources.ini" >nul
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\RunInstalledPreview.ps1" -FallbackLog "%~dp0build\logs\full-genesis-fallbacks.jsonl" -Preset native -SettingsDirectory "%~dp0settings\full-genesis" %*
set "TLK_RESULT=%errorlevel%"
if not "%TLK_RESULT%"=="0" pause
exit /b %TLK_RESULT%
