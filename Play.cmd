@echo off
setlocal
if not exist "%~dp0settings\the-best" mkdir "%~dp0settings\the-best"
if not exist "%~dp0settings\the-best\resources.ini" copy /Y "%~dp0profiles\the-best.ini" "%~dp0settings\the-best\resources.ini" >nul
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\RunInstalledPreview.ps1" -Preset native -SettingsDirectory "%~dp0settings\the-best" %*
set "TLK_RESULT=%errorlevel%"
if not "%TLK_RESULT%"=="0" pause
exit /b %TLK_RESULT%
