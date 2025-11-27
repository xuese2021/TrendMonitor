@echo off
chcp 65001 >nul
echo ============================================
echo    添加 RSS 源到 TrendMonitor
echo ============================================
echo.

set /p name="请输入源名称（如：机器之心）: "
set /p url="请输入 RSS 链接: "

echo.
echo 正在添加: %name%
echo 链接: %url%
echo.

echo %name%^|%url%^|true>> config\rss_feeds.txt

echo ✅ 已添加到 config\rss_feeds.txt
echo.
echo 请记得提交到 GitHub：
echo   git add config/rss_feeds.txt
echo   git commit -m "Add %name%"
echo   git push
echo.
pause

