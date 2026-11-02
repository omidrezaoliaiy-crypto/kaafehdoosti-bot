# -*- coding: utf-8 -*-
import subprocess
import time
import os

log_file = r"C:\KaafehDoostiBot\bot_console.log"

# Clear old log if exists or record length
start_len = 0
if os.path.exists(log_file):
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            start_len = len(f.read())
    except:
        pass

print("=== LAUNCHING SINGLE TEST PROCESS ===")
p = subprocess.Popen(
    [r"C:\Program Files\Python311\python.exe", "main.py"],
    cwd=r"C:\KaafehDoostiBot",
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print(f"BOT PID: {p.pid}")

print("Waiting 20 seconds for bot initialization & audio streaming...")
time.sleep(20)

print("=== READING BOT CONSOLE LOG ===")
new_content = ""
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        all_txt = f.read()
        new_content = all_txt[start_len:]

lines = [l.strip() for l in new_content.splitlines() if l.strip()]
print(f"Total new log lines: {len(lines)}")
for l in lines[-25:]:
    print(l[:95])

# Check for keywords
has_rejection = any("insertAudioBlock rejected" in l for l in lines)
has_pcm = any("PCM" in l or "play" in l.lower() or "track" in l.lower() for l in lines)
print(f"CHECK: Rejected errors = {has_rejection}")
print(f"CHECK: Audio/Playback detected = {has_pcm}")

print("=== TEST RUN COMPLETED ===")
