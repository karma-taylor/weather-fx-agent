@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境 .venv
    echo 请先在本文件夹打开 PowerShell，执行一次安装：
    echo   python -m venv .venv
    echo   .\.venv\Scripts\pip install -r requirements.txt
    echo 并复制 .env.example 为 .env，填入 OPENAI_API_KEY。
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "%~dp0agent.py"
echo.
pause
