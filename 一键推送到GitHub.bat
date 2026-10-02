@echo off
chcp 65001 >nul
title 推送项目到 GitHub - CalculationInLiDAR
color 0b
echo ===================================================================
echo   正在推送代码到 GitHub 仓库 (shinianshao/CalculationInLiDAR)...
echo ===================================================================
echo.
echo 提示：如果是首次推送，系统可能会弹出浏览器或凭据窗口请求 GitHub 授权。
echo       请在弹出的浏览器页面中点击 "Authorize" 即可完成授权。
echo.
cd /d "%~dp0"
git push -u origin main
echo.
if %errorlevel% equ 0 (
    color 0a
    echo ===================================================================
    echo   [SUCCESS] 项目已成功推送到 GitHub！
    echo   仓库主页: https://github.com/shinianshao/CalculationInLiDAR
    echo ===================================================================
) else (
    color 0c
    echo ===================================================================
    echo   [ERROR] 推送未完成，请检查网络连接或 GitHub 账号权限。
    echo ===================================================================
)
echo.
pause
