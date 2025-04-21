@echo off

:: Remove the task
schtasks /delete /tn "PassportMonitor" /f

if %ERRORLEVEL% equ 0 (
    echo Tarea eliminada exitosamente!
) else (
    echo Error al eliminar la tarea. Por favor, ejecuta este script como administrador.
)

pause 