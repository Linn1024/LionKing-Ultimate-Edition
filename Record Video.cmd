@echo off
setlocal
cd /d "%~dp0"
python "%~dp0tools\record_video.py" %*
set "TLK_RESULT=%errorlevel%"
pause
exit /b %TLK_RESULT%
