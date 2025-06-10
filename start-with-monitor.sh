#!/bin/bash
# filepath: ./start-with-monitor.sh
# Keeps restarting the bot unless shutdown.flag exists

set -e
cd "$(dirname "$0")"

# Remove shutdown.flag on first run
[ -f shutdown.flag ] && rm shutdown.flag

LOGFILE=bot_monitor.log

while true; do
    if [ -f shutdown.flag ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Shutdown flag detected. Exiting monitor." >> "$LOGFILE"
        exit 0
    fi
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting bot..." >> "$LOGFILE"
    python3 main.py
    status=$?
    if [ $status -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bot exited with error code $status. Restarting..." >> "$LOGFILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bot exited normally. Restarting..." >> "$LOGFILE"
    fi
    # Wait a bit before restart in case of crash
    sleep 5
done
