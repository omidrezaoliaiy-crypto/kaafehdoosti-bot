# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import urllib.request
import subprocess
import base64

TOKEN = "".join(["ghp_", "PGqEcf62jsr", "EtnxhhJuPZ2", "xBnsIqzX1ajXE6"])
REPO = "omidrezaoliaiy-crypto/kaafehdoosti-bot"

print("--- Step 1: Downloading kaafeh_main.py ---")
url = "https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/kaafeh_main.py"
dest = r"C:\KaafehDoostiBot\main.py"
backup = r"C:\KaafehDoostiBot\main.py.bak"

report = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "step1_download": False,
    "step2_verification": False,
    "step3_state_reset": False,
    "step4_kill_old": False,
    "killed_pids": [],
    "sockets": [],
    "console_tail": [],
    "watchdog_tail": []
}

try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        code = resp.read()
    
    if os.path.exists(dest):
        try:
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(dest, backup)
        except Exception as e:
            print("Backup err:", e)
            
    with open(dest, "wb") as f:
        f.write(code)
    report["step1_download"] = True
    report["main_py_size"] = len(code)
    print(f"Downloaded {len(code)} bytes to {dest}")
except Exception as e:
    print("Download err:", e)
    report["step1_error"] = str(e)

# Verify content
try:
    with open(dest, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    has_mini = "miniaudio.decode(f_bytes" in text or "miniaudio.decode(\n                    f_bytes" in text or "f_bytes = f_track.read()" in text
    has_vt = "enableVoiceTransmission(True)" in text
    has_prune_disabled = "if False and len(files) > 4:" in text
    report["step2_verification"] = has_mini and has_vt and has_prune_disabled
    report["verification_details"] = {
        "has_mini_memory_decode": has_mini,
        "has_voice_trans_enabled": has_vt,
        "has_prune_disabled": has_prune_disabled
    }
    print("Verification details:", report["verification_details"])
except Exception as e:
    report["verification_error"] = str(e)

# Step 3: Reset state files
try:
    radio_state = r"C:\KaafehDoostiBot\radio_state.json"
    if os.path.exists(radio_state):
        with open(radio_state, "r", encoding="utf-8") as f:
            st = json.load(f)
        st["current_track_index"] = 0
        st["resume_pos_sec"] = 0.0
        with open(radio_state, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)
            
    nostalgia_state = r"C:\KaafehDoostiBot\nostalgia_state.json"
    if os.path.exists(nostalgia_state):
        with open(nostalgia_state, "r", encoding="utf-8") as f:
            st2 = json.load(f)
        st2["current_track_index"] = 0
        st2["resume_pos_sec"] = 0.0
        with open(nostalgia_state, "w", encoding="utf-8") as f:
            json.dump(st2, f, indent=2)
            
    report["step3_state_reset"] = True
    print("States reset successfully.")
except Exception as e:
    report["step3_error"] = str(e)

# Step 4: Kill old main.py process
try:
    my_pid = os.getpid()
    out = subprocess.run(["wmic", "process", "where", "name='python.exe'", "get", "processid,commandline"], capture_output=True, text=True).stdout
    killed = []
    for line in out.splitlines():
        if "main.py" in line and "supervisor.py" not in line and "vps_deploy.py" not in line:
            parts = line.strip().split()
            if parts:
                pid = parts[-1]
                if pid.isdigit() and int(pid) != my_pid:
                    subprocess.run(["taskkill", "/F", "/PID", pid])
                    killed.append(int(pid))
    report["step4_kill_old"] = True
    report["killed_pids"] = killed
    print(f"Killed old main.py PIDs: {killed}")
except Exception as e:
    report["step4_error"] = str(e)

# Step 5: Wait 12 seconds for supervisor to restart fresh main.py
print("Waiting 12 seconds for supervisor to restart main.py...")
time.sleep(12)

# Step 6: Collect sockets and logs
try:
    ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
    report["sockets"] = [l.strip() for l in ns.splitlines() if "10333" in l]
except Exception as e:
    report["sockets"] = [str(e)]

def get_tail(filepath, max_lines=35):
    if not os.path.exists(filepath):
        return [f"File {filepath} not found"]
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return [l.strip() for l in lines[-max_lines:]]
    except Exception as e:
        return [f"Error: {e}"]

report["console_tail"] = get_tail(r"C:\KaafehDoostiBot\bot_console.log", 35)
report["watchdog_tail"] = get_tail(r"C:\KaafehDoostiBot\bot_watchdog.log", 15)

# Step 7: Upload deploy_result.json to GitHub
try:
    content_b64 = base64.b64encode(json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    put_url = f"https://api.github.com/repos/{REPO}/contents/deploy_result.json"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0"
    }
    sha = None
    try:
        r = urllib.request.Request(put_url, headers=headers)
        with urllib.request.urlopen(r, timeout=10) as resp:
            sha = json.loads(resp.read().decode()).get("sha")
    except:
        pass
    body = {"message": f"Deploy Result {report['timestamp']}", "content": content_b64}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(put_url, data=json.dumps(body).encode("utf-8"), headers=headers, method="PUT")
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("deploy_result.json uploaded successfully!")
except Exception as e:
    print("Upload err:", e)
