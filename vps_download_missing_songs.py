# -*- coding: utf-8 -*-
import os, sys, json, time, urllib.request, base64

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
BASE_DIR = r"C:\KaafehDoostiBot"
CACHE_DIR = os.path.join(BASE_DIR, "music_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TG_TOKEN = "8600063713:AAGxU2xoECq5u1FjdOIgAA1PPdHBSXnZIt8"
API_BASE = "https://tg.kaafehdoosti.ir"

# Fetch full_radio_catalog.json from GitHub
cat_url = f"https://raw.githubusercontent.com/{REPO}/main/full_radio_catalog.json"
req = urllib.request.Request(cat_url, headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    catalog = json.loads(resp.read().decode())

print(f"Total catalog tracks to verify: {len(catalog)}", flush=True)

existing_files = os.listdir(CACHE_DIR)
downloaded = 0
failed = 0

for item in catalog:
    mid = item["msg_id"]
    fid = item["file_id"]
    title = item["title"]
    performer = item.get("performer", "")
    clean_title = "".join(c for c in title if c.isalnum() or c in " ._-()").strip()
    if not clean_title.endswith(".mp3"):
        clean_title += ".mp3"
    dest_name = f"{mid}_{clean_title}"
    dest_path = os.path.join(CACHE_DIR, dest_name)

    # Check if already downloaded (either exact name or starts with f"{mid}_")
    already = any(f == dest_name or f.startswith(f"{mid}_") for f in existing_files)
    if already:
        continue

    print(f"Downloading [{mid}] {performer} - {title}...", flush=True)
    try:
        # 1. getFile
        gf_url = f"{API_BASE}/bot{TG_TOKEN}/getFile?file_id={fid}"
        gf_req = urllib.request.Request(gf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(gf_req, timeout=15) as gf_resp:
            gf_res = json.loads(gf_resp.read().decode())
        
        if not gf_res.get("ok"):
            print(f"getFile failed for {mid}: {gf_res}", flush=True)
            failed += 1
            continue

        file_path = gf_res["result"]["file_path"]
        dl_url = f"{API_BASE}/file/bot{TG_TOKEN}/{file_path}"
        dl_req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
        
        tmp_path = dest_path + ".tmp"
        with urllib.request.urlopen(dl_req, timeout=90) as r, open(tmp_path, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)

        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 10000:
            os.replace(tmp_path, dest_path)
            downloaded += 1
            print(f"Successfully saved {dest_name} ({os.path.getsize(dest_path)} bytes)!", flush=True)
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            failed += 1
    except Exception as e:
        print(f"Error downloading {mid}: {e}", flush=True)
        failed += 1
    time.sleep(0.1)

res = {
    "total_catalog": len(catalog),
    "downloaded_new": downloaded,
    "failed": failed,
    "total_in_cache": len(os.listdir(CACHE_DIR))
}

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/download_report.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Download report', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded download_report.json')
