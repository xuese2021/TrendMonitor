@echo off
chcp 65001 >nul
echo ============================================
echo    RSS 添加 Bot - Telegram 一键添加
echo ============================================
echo.

if "%ADD_RSS_BOT_TOKEN%"=="" (
    echo ❌ 请先设置环境变量 ADD_RSS_BOT_TOKEN
    echo.
    echo 步骤：
    echo 1. 在 Telegram 找 @BotFather
    echo 2. 发送 /newbot 创建新 Bot
    echo 3. 复制获得的 Token
    echo 4. 运行以下命令设置环境变量：
    echo.
    echo    set ADD_RSS_BOT_TOKEN=你的Token
    echo.
    echo 或者在系统环境变量中永久设置
    echo.
    pause
    exit /b
)

echo ✅ Token 已配置
echo 🚀 启动 Bot...
echo.
echo 在 Telegram 中发送 RSS 链接给你的 Bot
echo 按 Ctrl+C 停止
echo.

python telegram_add_rss.py
pause

