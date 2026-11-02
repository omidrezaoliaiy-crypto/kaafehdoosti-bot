# -*- coding: utf-8 -*-
import os
import subprocess
import time
import sys

BASE_DIR = r"C:\KaafehDoostiBot"
PYTHON_EXE = r"C:\Program Files\Python311\python.exe"
MAIN_PY = os.path.join(BASE_DIR, "main.py")
CONSOLE_LOG = os.path.join(BASE_DIR, "bot_console.log")
SUPERVISOR_LOG = os.path.join(BASE_DIR, "bot_watchdog.log")

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    print(line, end="", flush=True)
    try:
        with open(SUPERVISOR_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except:
        pass

log("Supervisor service initialized.")

while True:
    log("Starting Kaafeh Doosti main.py...")
    try:
        with open(CONSOLE_LOG, "a", encoding="utf-8") as out:
            p = subprocess.Popen(
                [PYTHON_EXE, MAIN_PY],
                cwd=BASE_DIR,
                stdout=out,
                stderr=subprocess.STDOUT
            )
            log(f"Bot process started with PID {p.pid}")
            p.wait()
            log(f"Bot process exited with code {p.returncode}. Restarting in 5s...")
    except Exception as e:
        log(f"Supervisor error: {e}. Retrying in 5s...")
    time.sleep(5)
