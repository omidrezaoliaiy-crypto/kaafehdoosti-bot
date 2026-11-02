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
            chunk = resp.read(2 * 1024 * 1024) # 2MB
            if not chunk:
                break
            out.write(chunk)
            total += len(chunk)
    log(f"Download OK ({total} bytes)")
    return total

def main():
    log("=== STARTING FULL VPS MUSIC & BOT DEPLOYMENT ===")

    dest = r"C:\KaafehDoostiBot"
    os.makedirs(os.path.join(dest, "music_cache"), exist_ok=True)
    os.makedirs(os.path.join(dest, "music_cache_nostalgia"), exist_ok=True)

    # 1. Update main.py
    log("Step 1: Updating main.py...")
    try:
        download_file("https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py", r"C:\KaafehDoostiBot\main.py")
    except Exception as e:
        log(f"Err updating main.py: {e}")

    # 2. Check if music bundle is already downloaded
    zip_path = r"C:\music_bundle.zip"
    bundle_url = "https://github.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/releases/download/v1.0.0/music_bundle.zip"
    
    if os.path.exists(zip_path) and os.path.getsize(zip_path) == 404727535:
        log("Step 2: Music bundle already downloaded (404,727,535 bytes). Skipping download!")
    else:
        log("Step 2: Downloading music bundle (385 MB)...")
        t0 = time.time()
        download_file(bundle_url, zip_path)
        log(f"Music bundle downloaded in {int(time.time() - t0)}s.")

    # 3. Extract safely into C:\KaafehDoostiBot without touching locked existing files
    log("Step 3: Extracting all tracks into KaafehDoostiBot...")
    t1 = time.time()
    extracted_count = 0
    skipped_count = 0

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            target_path = os.path.join(dest, member.filename)
            if member.is_dir():
                os.makedirs(target_path, exist_ok=True)
                continue
            
            # If already exists and valid size, skip to avoid locking issues
            if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                skipped_count += 1
                continue

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as source, open(target_path, 'wb') as target:
                target.write(source.read())
            extracted_count += 1

    log(f"Extraction done in {int(time.time() - t1)}s! Extracted {extracted_count} new files, skipped {skipped_count} existing.")

    try:
        os.remove(zip_path)
        log("Zip file removed.")
    except Exception as e:
        log(f"Note on zip remove: {e}")

    # 4. Verify counts
    radio_dir = os.path.join(dest, "music_cache")
    nostalgia_dir = os.path.join(dest, "music_cache_nostalgia")
    radio_count = len([f for f in os.listdir(radio_dir) if f.lower().endswith('.mp3')])
    nostalgia_count = len([f for f in os.listdir(nostalgia_dir) if f.lower().endswith('.mp3')])

    log(f"VERIFIED_FILES: RADIO={radio_count} NOSTALGIA={nostalgia_count}")

    # 5. Restart Python bot cleanly so it loads the full 56-track library
    log("Step 4: Restarting bot to load full playlist...")
    my_pid = os.getpid()
    subprocess.run([
        "powershell", "-Command",
        f"Get-Process python -ErrorAction SilentlyContinue | Where-Object {{ $_.Id -ne {my_pid} }} | Stop-Process -Force"
    ], capture_output=True)

    time.sleep(4)

    # If watchdog doesn't immediately restart it, ensure it's running
    procs_out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True)
    if procs_out.stdout.count("python.exe") <= 1:
        subprocess.Popen(["cmd.exe", "/c", "start", "KaafehDoosti", "/min", r"C:\KaafehDoostiBot\start_bot.bat"], shell=True)
        time.sleep(3)

    final_procs = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True).stdout.count("python.exe")

    # Final completion marker
    print(f"DEPLOY_ALL_OK RADIO={radio_count} NOSTALGIA={nostalgia_count} PROCS={final_procs} FINISHED", flush=True)

if __name__ == "__main__":
    main()
