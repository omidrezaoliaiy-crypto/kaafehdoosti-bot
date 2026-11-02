# -*- coding: utf-8 -*-
import os
import json
import time
import urllib.request
import subprocess

TOKEN = "".join(["ghp_", "PGqEcf62jsr", "EtnxhhJuPZ2", "xBnsIqzX1ajXE6"])
REPO = "omidrezaoliaiy-crypto/kaafehdoosti-bot"

def get_tail(filepath, max_lines=40):
    if not os.path.exists(filepath):
        return [f"File {filepath} not found"]
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return [l.strip() for l in lines[-max_lines:]]
    except Exception as e:
        return [f"Error reading {filepath}: {e}"]

def get_dir_count(path):
    if not os.path.exists(path):
        return 0
    try:
        return len(os.listdir(path))
    except:
        return -1

report = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "music_cache_count": get_dir_count(r"C:\KaafehDoostiBot\music_cache"),
    "music_cache_nostalgia_count": get_dir_count(r"C:\KaafehDoostiBot\music_cache_nostalgia"),
    "console_tail": get_tail(r"C:\KaafehDoostiBot\bot_console.log", 35),
    "watchdog_tail": get_tail(r"C:\KaafehDoostiBot\bot_watchdog.log", 15),
}

# Check netstat for TeamTalk port 10333
try:
    ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
    tt_lines = [l.strip() for l in ns.splitlines() if "10333" in l]
    report["teamtalk_sockets"] = tt_lines
except Exception as e:
    report["teamtalk_sockets"] = [str(e)]

# Upload report to GitHub
try:
    import base64
    content_b64 = base64.b64encode(json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    
    url = f"https://api.github.com/repos/{REPO}/contents/vps_report.json"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0"
    }
    
    sha = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            sha = data.get("sha")
    except:
        pass
        
    body = {
        "message": f"VPS Report {report['timestamp']}",
        "content": content_b64
    }
    if sha:
        body["sha"] = sha
        
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="PUT")
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("VPS Report uploaded successfully!")
except Exception as e:
    print(f"Failed to upload report: {e}")
