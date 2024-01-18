#!/bin/bash
while true
do
    python3 main.py >> main.log 2>&1
    sleep 1
done