@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PY_BIN="

if exist "%USERPROFILE%\miniforge3\python.exe" (
    set "PY_BIN=%USERPROFILE%\miniforge3\python.exe"
    goto :FOUND
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :FOUND
)
if exist "%USERPROFILE%\miniconda3\python.exe" (
    set "PY_BIN=%USERPROFILE%\miniconda3\python.exe"
    goto :FOUND
)
if exist "%USERPROFILE%\anaconda3\python.exe" (
    set "PY_BIN=%USERPROFILE%\anaconda3\python.exe"
    goto :FOUND
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_BIN=python"
    goto :FOUND
)

echo [ERROR] Python not found on system.
pause
exit /b 1

:FOUND
echo [OK] Using Python: !PY_BIN!
echo Starting Desktop GUI in independent window...
start "" "!PY_BIN!" launch_raman_app.py
exit /b 0
