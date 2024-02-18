#!/bin/bash

# Path to your main.py
MAIN_PY_PATH="./main.py"

# Function to kill and restart main.py
restart_main_py() {
    pkill -f "python3 $MAIN_PY_PATH"
    python3 "$MAIN_PY_PATH" &
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