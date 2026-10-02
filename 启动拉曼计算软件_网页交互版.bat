@echo off
cd /d "%~dp0"
echo [OK] Opening Interactive Raman Spectroscopy Web App in default browser...
start "" "%~dp0raman_interactive.html"
exit /b 0
