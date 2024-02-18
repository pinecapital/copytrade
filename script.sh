#!/bin/bash

# Path to your main.py
MAIN_PY_PATH="./main.py"

# Function to kill and restart main.py
restart_main_py() {
    pkill -f "python3 $MAIN_PY_PATH"
    python3 "$MAIN_PY_PATH" &
}

# Function to calculate sleep time until 8 AM
get_sleep_time() {
    local current_epoch=$(date +%s)
    local target_epoch=$(date -d 'tomorrow 08:00' +%s)
    echo $(($target_epoch - $current_epoch))
}

# If the first command-line argument is "restart", then restart main.py
if [ "$1" = "restart" ]; then
    restart_main_py
    exit 0
fi

# Watch for modifications to config.json
while inotifywait -e modify ./config.json; do
    restart_main_py
done &

# Sleep until 8 AM and then restart main.py
while true; do
    sleep $(get_sleep_time)
    restart_main_py
done &