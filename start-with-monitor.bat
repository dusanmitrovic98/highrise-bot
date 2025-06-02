@echo off
REM monitor.bat - Keeps restarting the bot unless shutdown.flag exists

setlocal enabledelayedexpansion
cd /d %~dp0

REM Remove shutdown.flag on first run
if exist shutdown.flag del shutdown.flag

:loop
if exist shutdown.flag (
    echo Shutdown flag detected. Exiting monitor.
    exit /b 0
)
echo Starting bot...
call python main.py
REM Wait a bit before restart in case of crash
ping -n 6 127.0.0.1 > nul

goto loop
