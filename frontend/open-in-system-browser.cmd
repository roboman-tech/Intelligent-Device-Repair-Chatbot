@echo off
set "URL=http://127.0.0.1:5173/"
REM Opens Edge/Chrome by EXE path so Windows "default browser" cannot send http:// to Cursor.

if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
  start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --new-window "%URL%"
  exit /b 0
)
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
  start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" --new-window "%URL%"
  exit /b 0
)
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
  start "" "%LocalAppData%\Google\Chrome\Application\chrome.exe" --new-window "%URL%"
  exit /b 0
)
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
  start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --new-window "%URL%"
  exit /b 0
)

echo Could not find Edge or Chrome. Fix: Settings - Apps - Default apps - set Edge or Chrome for HTTP/HTTPS.
echo Then open this in the address bar: %URL%
pause
exit /b 1
