# -*- coding: utf-8 -*-
import os
import subprocess
import time
import sys

# Ensure TeamTalk bots are enabled on VPS 24/7 supervisor
os.environ["ENABLE_TT_BOTS"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

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

log("Supervisor service initialized with ENABLE_TT_BOTS=1.")

while True:
    log("Starting Kaafeh Doosti main.py via Supervisor...")
    try:
        with open(CONSOLE_LOG, "a", encoding="utf-8") as out:
            env = os.environ.copy()
            env["ENABLE_TT_BOTS"] = "1"
            p = subprocess.Popen(
                [PYTHON_EXE, MAIN_PY],
                cwd=BASE_DIR,
                stdout=out,
                stderr=subprocess.STDOUT,
                env=env
            )
            log(f"Bot process started with PID {p.pid}")
            p.wait()
            log(f"Bot process exited with code {p.returncode}. Restarting in 5s...")
    except Exception as e:
        log(f"Supervisor error: {e}. Retrying in 5s...")
    time.sleep(5)
