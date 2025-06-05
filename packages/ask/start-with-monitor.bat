@echo off
REM monitor.bat - Keeps restarting the groq_chat server unless shutdown.flag exists

setlocal enabledelayedexpansion
cd /d %~dp0

REM Remove shutdown.flag on first run
if exist shutdown.flag del shutdown.flag

set LOGFILE=groq_monitor.log

:loop
if exist shutdown.flag (
    echo [%date% %time%] Shutdown flag detected. Exiting monitor. >> %LOGFILE%
    exit /b 0
)
echo [%date% %time%] Starting groq_chat server... >> %LOGFILE%
call python main.py
if %errorlevel% neq 0 (
    echo [%date% %time%] groq_chat exited with error code %errorlevel%. Restarting... >> %LOGFILE%
) else (
    echo [%date% %time%] groq_chat exited normally. Restarting... >> %LOGFILE%
)
REM Wait a bit before restart in case of crash
ping -n 6 127.0.0.1 > nul

goto loop
