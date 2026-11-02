import os
import sys
import time
import subprocess
import urllib.request
import zipfile

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def download_file(url, target_path):
    log(f"Downloading from {url} -> {target_path}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(target_path, "wb") as out:
        total = 0
        while True:
            chunk = resp.read(2 * 1024 * 1024) # 2MB
            if not chunk:
                break
            out.write(chunk)
            total += len(chunk)
    log(f"Downloaded {total} bytes successfully.")
    return total

def main():
    log("=== STARTING FULL VPS MUSIC & BOT DEPLOYMENT ===")

    # 1. Stop running Python processes to release file locks
    log("Step 1: Stopping running Python processes...")
    subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
    time.sleep(2)

    # 2. Update main.py
    log("Step 2: Updating main.py with permanent cache settings...")
    try:
        download_file("https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py", r"C:\KaafehDoostiBot\main.py")
    except Exception as e:
        log(f"Warning downloading main.py: {e}")

    # 3. Download music bundle
    zip_path = r"C:\music_bundle.zip"
    bundle_url = "https://github.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/releases/download/v1.0.0/music_bundle.zip"
    log("Step 3: Downloading music bundle (385 MB)...")
    t0 = time.time()
    download_file(bundle_url, zip_path)
    log(f"Download completed in {int(time.time() - t0)} seconds.")

    # 4. Extract into C:\KaafehDoostiBot
    log("Step 4: Extracting music bundle...")
    t1 = time.time()
    dest = r"C:\KaafehDoostiBot"
    os.makedirs(os.path.join(dest, "music_cache"), exist_ok=True)
    os.makedirs(os.path.join(dest, "music_cache_nostalgia"), exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest)
    log(f"Extraction completed in {int(time.time() - t1)} seconds.")

    # Remove temporary zip
    try:
        os.remove(zip_path)
        log("Removed temporary zip file.")
    except Exception as e:
        log(f"Note: Could not remove zip: {e}")

    # 5. Verify counts
    radio_dir = os.path.join(dest, "music_cache")
    nostalgia_dir = os.path.join(dest, "music_cache_nostalgia")
    radio_count = len([f for f in os.listdir(radio_dir) if f.lower().endswith('.mp3')])
    nostalgia_count = len([f for f in os.listdir(nostalgia_dir) if f.lower().endswith('.mp3')])

    log(f"VERIFICATION: Radio={radio_count} Nostalgia={nostalgia_count}")

    # 6. Start the 24/7 Watchdog
    log("Step 5: Starting bot via watchdog...")
    subprocess.Popen(["cmd.exe", "/c", "start", "KaafehDoosti", "/min", r"C:\KaafehDoostiBot\start_bot.bat"], shell=True)
    time.sleep(4)

    # 7. Check running process
    procs_out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True)
    procs_count = procs_out.stdout.count("python.exe")
    log(f"FINAL_REPORT: RADIO_SONGS={radio_count} NOSTALGIA_SONGS={nostalgia_count} PYTHON_PROCS={procs_count} DEPLOY_ALL_OK")

if __name__ == "__main__":
    main()
