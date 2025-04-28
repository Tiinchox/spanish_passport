@echo off

:: Remove the task
schtasks /delete /tn "PassportMonitor" /f

if %ERRORLEVEL% equ 0 (
    echo Task removed successfully!
) else (
    echo Error removing task. Please run this script as administrator.
)

pause 