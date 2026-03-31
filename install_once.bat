@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] 创建虚拟环境 .venv ...
python -m venv .venv
if errorlevel 1 (
    echo 失败：请确认已安装 Python 并已加入 PATH。
    pause
    exit /b 1
)

echo [2/3] 安装依赖 ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo [3/3] 已复制 .env.example 为 .env
        echo       请用记事本打开 .env，填入 OPENAI_API_KEY 后保存。
    ) else (
        echo [3/3] 未找到 .env.example，请手动创建 .env 并配置 OPENAI_API_KEY。
    )
) else (
    echo [3/3] 已存在 .env，跳过复制。
)

echo.
echo 完成。以后双击 start.bat 即可启动 Agent。
pause
