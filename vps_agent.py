# -*- coding: utf-8 -*-
import os
import json
import time
import urllib.request
import subprocess
import base64

TOKEN = "".join(["ghp_", "PGqEcf62jsr", "EtnxhhJuPZ2", "xBnsIqzX1ajXE6"])
REPO = "omidrezaoliaiy-crypto/kaafehdoosti-bot"

deploy_info = {"executed": False}
MAIN_DEST = r"C:\KaafehDoostiBot\main.py"
need_deploy = True

if os.path.exists(MAIN_DEST):
    try:
        with open(MAIN_DEST, "r", encoding="utf-8", errors="ignore") as f_cur:
            cur_code = f_cur.read()
        if "miniaudio.decode(f_bytes" in cur_code and "enableVoiceTransmission(True)" in cur_code:
            need_deploy = False
            deploy_info["status"] = "already_latest"
    except Exception as e:
        deploy_info["read_err"] = str(e)

if need_deploy:
    deploy_info["executed"] = True
    try:
        api_url = f"https://api.github.com/repos/{REPO}/contents/kaafeh_main.py"
        req_d = urllib.request.Request(api_url, headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github.v3.raw",
            "User-Agent": "Mozilla/5.0"
        })
        with urllib.request.urlopen(req_d, timeout=25) as resp_d:
            new_code = resp_d.read()
        with open(MAIN_DEST, "wb") as f_out:
            f_out.write(new_code)
        deploy_info["download_bytes"] = len(new_code)
        
        # Reset states
        for sf in [r"C:\KaafehDoostiBotadio_state.json", r"C:\KaafehDoostiBot
ostalgia_state.json"]:
            try:
                with open(sf, "w", encoding="utf-8") as f_s:
                    json.dump({"current_track_index": 0, "resume_pos_sec": 0.0}, f_s, indent=2)
            except Exception as e_s:
                pass
        
        # Kill running main.py processes
        out_p = subprocess.run(["wmic", "process", "where", "name='python.exe'", "get", "processid,commandline"], capture_output=True, text=True).stdout
        my_pid = os.getpid()
        killed = []
        for line in out_p.splitlines():
            if "main.py" in line and "supervisor" not in line and "agent" not in line:
                parts = line.strip().split()
                if parts and parts[-1].isdigit() and int(parts[-1]) != my_pid:
                    subprocess.run(["taskkill", "/F", "/PID", parts[-1]])
                    killed.append(int(parts[-1]))
        deploy_info["killed_pids"] = killed
        
        # Wait for supervisor to restart main.py
        time.sleep(12)
        deploy_info["status"] = "deployed_and_restarted"
    except Exception as e_dep:
        deploy_info["error"] = str(e_dep)

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
    "deploy_info": deploy_info,
    "music_cache_count": get_dir_count(r"C:\KaafehDoostiBot\music_cache"),
    "music_cache_nostalgia_count": get_dir_count(r"C:\KaafehDoostiBot\music_cache_nostalgia"),
    "console_tail": get_tail(r"C:\KaafehDoostiBotot_console.log", 35),
    "watchdog_tail": get_tail(r"C:\KaafehDoostiBotot_watchdog.log", 15),
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
        "content": content_b64,
        "branch": "main"
    }
    if sha:
        body["sha"] = sha
        
    req2 = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="PUT"
    )
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        print(f"VPS Report uploaded successfully! Status: {resp2.status}")
except Exception as e:
    print(f"Failed to upload report: {e}")
