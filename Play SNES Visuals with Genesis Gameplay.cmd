@echo off
setlocal
if not exist "%~dp0settings\snes-visuals-genesis" mkdir "%~dp0settings\snes-visuals-genesis"
if not exist "%~dp0settings\snes-visuals-genesis\resources.ini" copy /Y "%~dp0profiles\snes-visuals-genesis.ini" "%~dp0settings\snes-visuals-genesis\resources.ini" >nul
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\RunInstalledPreview.ps1" -Preset native -SettingsDirectory "%~dp0settings\snes-visuals-genesis" %*
set "TLK_RESULT=%errorlevel%"
if not "%TLK_RESULT%"=="0" pause
exit /b %TLK_RESULT%
