import socket
import struct
import os
import zipfile
import sys
import time

PORT = 9000
ZIP_PATH = r"C:\KaafehDoostiBot\nostalgia_235.zip"
TARGET_DIR = r"C:\KaafehDoostiBot\music_cache_nostalgia"

os.makedirs(TARGET_DIR, exist_ok=True)

print(f"[Receiver] Starting direct TCP receiver on port {PORT}...", flush=True)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', PORT))
s.listen(1)
print(f"[Receiver] Listening on 0.0.0.0:{PORT}, waiting for connection from host...", flush=True)

conn, addr = s.accept()
print(f"[Receiver] Connection accepted from {addr}!", flush=True)

# Read 8 bytes file length
header = b""
while len(header) < 8:
    chunk = conn.recv(8 - len(header))
    if not chunk:
        break
    header += chunk

if len(header) < 8:
    print("[Receiver] Failed to read header!", flush=True)
    conn.close()
    s.close()
    sys.exit(1)

total_size = struct.unpack("!Q", header)[0]
print(f"[Receiver] Expecting {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)...", flush=True)

received = 0
t0 = time.time()
last_report = t0

with open(ZIP_PATH, "wb") as f:
    while received < total_size:
        to_read = min(1024 * 1024, total_size - received)
        chunk = conn.recv(to_read)
        if not chunk:
            break
        f.write(chunk)
        received += len(chunk)
        now = time.time()
        if now - last_report > 5:
            last_report = now
            pct = (received / total_size) * 100
            mb = received / (1024 * 1024)
            speed = (received / (now - t0)) / (1024 * 1024)
            print(f"[Receiver] {mb:.1f} MB / {total_size/(1024*1024):.1f} MB ({pct:.1f}%) at {speed:.2f} MB/s", flush=True)

elapsed = time.time() - t0
print(f"[Receiver] Received {received:,} bytes in {elapsed:.1f}s (average {(received/elapsed)/(1024*1024):.2f} MB/s)!", flush=True)

conn.sendall(b"OK_RECEIVED\n")
conn.close()
s.close()

if received == total_size:
    print(f"[Receiver] File integrity verified. Extracting into {TARGET_DIR}...", flush=True)
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        z.extractall(TARGET_DIR)
    print(f"[Receiver] Extraction complete! Verifying files...", flush=True)
    mp3_files = [f for f in os.listdir(TARGET_DIR) if f.endswith('.mp3')]
    print(f"[Receiver] Total MP3 files in {TARGET_DIR}: {len(mp3_files)}", flush=True)
    try:
        os.remove(ZIP_PATH)
        print(f"[Receiver] Removed temporary zip file.", flush=True)
    except:
        pass
    print("[Receiver] ALL DONE SUCCESSFULLY!", flush=True)
else:
    print(f"[Receiver] Incomplete transfer: {received} != {total_size}", flush=True)
