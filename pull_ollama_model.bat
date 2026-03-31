@echo off
chcp 65001 >nul
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not exist "%OLLAMA%" (
    echo 未找到 Ollama：%OLLAMA%
    echo 请从开始菜单启动过一次 Ollama，或检查安装路径。
    pause
    exit /b 1
)
echo 将下载模型（体积较大，请耐心等待）：llama3.2:3b
echo 若希望更强懂工具调用，可改用：llama3.1:8b（更大更慢）
echo.
"%OLLAMA%" pull llama3.2:3b
echo.
echo 完成后请把 .env 里三行改成 Ollama（见 .env.example 方案 3），MODEL 写：llama3.2:3b
pause
