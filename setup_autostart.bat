@echo off
setlocal enabledelayedexpansion

:: Get the current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%main.py"

echo Script directory: "%SCRIPT_DIR%"
echo Script path: "%SCRIPT_PATH%"

:: Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo Error: main.py file not found in "%SCRIPT_PATH%"
    pause
    exit /b 1
)

:: Check if virtual environment exists and set Python path
if exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    echo Virtual environment found
    set "PYTHON_CMD=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
    echo Warning: No virtual environment found, using system Python
    echo It is recommended to create a virtual environment first:
    echo python -m venv .venv
    echo .venv\Scripts\activate
    echo pip install -r requirements.txt
    set "PYTHON_CMD=python"
)

:: Remove existing task if it exists
echo Removing existing task if present...
schtasks /delete /tn "PassportMonitor" /f >nul 2>&1

:: Create the task with full path
echo Creating scheduled task...
echo Command to execute: "%PYTHON_CMD%" "%SCRIPT_PATH%"

schtasks /create /tn "PassportMonitor" /tr "\"%PYTHON_CMD%\" \"%SCRIPT_PATH%\"" /sc onlogon /ru %USERNAME% /rl HIGHEST /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo Task created successfully!
    echo.
    echo Verifying task...
    schtasks /query /tn "PassportMonitor" /fo list /v
) else (
    echo.
    echo Error creating task. Error code: %ERRORLEVEL%
    echo Please run this script as administrator.
    echo.
    echo Try running the following command manually as administrator:
    echo schtasks /create /tn "PassportMonitor" /tr "\"%PYTHON_CMD%\" \"%SCRIPT_PATH%\"" /sc onlogon /ru %USERNAME% /rl HIGHEST /f
)

echo.
echo Press any key to continue...
pause >nul 