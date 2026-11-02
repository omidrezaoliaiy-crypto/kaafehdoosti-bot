import os
import sys
import time
import subprocess
import urllib.request
import zipfile

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def download_file(url, target_path):
    log(f"Downloading: {target_path} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(target_path, "wb") as out:
        total = 0
        while True:
            chunk = resp.read(2 * 1024 * 1024) # 2MB chunks
            if not chunk:
                break
            out.write(chunk)
            total += len(chunk)
    log(f"Download OK ({total} bytes)")
    return total

def main():
    log("STARTING_EXTRACTION_SCRIPT")

    # 1. Stop bot processes EXCEPT this script
    my_pid = os.getpid()
    log(f"Stopping other Python processes (excluding PID {my_pid})...")
    subprocess.run([
        "powershell", "-Command",
        f"Get-Process python -ErrorAction SilentlyContinue | Where-Object {{ $_.Id -ne {my_pid} }} | Stop-Process -Force"
    ], capture_output=True)
    time.sleep(2)

    # 2. Update main.py
    log("Step 2: Updating main.py...")
    try:
        download_file("https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py", r"C:\KaafehDoostiBot\main.py")
    except Exception as e:
        log(f"Err updating main.py: {e}")

    # 3. Download music bundle
    zip_path = r"C:\music_bundle.zip"
    bundle_url = "https://github.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/releases/download/v1.0.0/music_bundle.zip"
    log("Step 3: Downloading music bundle (385 MB)...")
    t0 = time.time()
    download_file(bundle_url, zip_path)
    log(f"Music bundle downloaded in {int(time.time() - t0)}s.")

    # 4. Extract into C:\KaafehDoostiBot
    dest = r"C:\KaafehDoostiBot"
    os.makedirs(os.path.join(dest, "music_cache"), exist_ok=True)
    os.makedirs(os.path.join(dest, "music_cache_nostalgia"), exist_ok=True)

    log("Step 4: Extracting zip...")
    t1 = time.time()
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest)
    log(f"Extracted all in {int(time.time() - t1)}s.")

    try:
        os.remove(zip_path)
        log("Zip removed.")
    except Exception:
        pass

    # 5. Verify counts
    radio_dir = os.path.join(dest, "music_cache")
    nostalgia_dir = os.path.join(dest, "music_cache_nostalgia")
    radio_count = len([f for f in os.listdir(radio_dir) if f.lower().endswith('.mp3')])
    nostalgia_count = len([f for f in os.listdir(nostalgia_dir) if f.lower().endswith('.mp3')])

    log(f"VERIFIED: RADIO={radio_count} NOSTALGIA={nostalgia_count}")

    # 6. Start the 24/7 Watchdog
    log("Step 5: Starting bot via watchdog...")
    subprocess.Popen(["cmd.exe", "/c", "start", "KaafehDoosti", "/min", r"C:\KaafehDoostiBot\start_bot.bat"], shell=True)
    time.sleep(4)

    procs_out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True)
    procs_count = procs_out.stdout.count("python.exe")

    # Final completion marker
    print(f"DEPLOY_ALL_OK RADIO={radio_count} NOSTALGIA={nostalgia_count} PROCS={procs_count}", flush=True)

if __name__ == "__main__":
    main()
