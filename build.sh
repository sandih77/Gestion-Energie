#! /bin/bash

run () {
    source /home/sandih/env/bin/activate
    echo "---RUNNING---"
    python3 src/Main.py
    deactivate
}

run