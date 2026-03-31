@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv\Scripts\python.exe not found.
    echo Run install_once.bat first.
    pause
    exit /b 1
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

set "IPADDR="
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /R /C:"IPv4"') do (
    set "IPADDR=%%i"
    goto :ipok
)

:ipok
set "IPADDR=%IPADDR: =%"
echo.
echo Web server starting...
echo Local: http://127.0.0.1:8000
if defined IPADDR echo LAN:   http://%IPADDR%:8000
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" -m uvicorn webapp:app --host 0.0.0.0 --port 8000
pause
