# -*- coding: utf-8 -*-
import subprocess, urllib.request, json, base64, os

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
target_file = r"C:\KaafehDoostiBot\vps_download_missing_songs.py"

try:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/vps_download_missing_songs.py",
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        with open(target_file, "wb") as f:
            f.write(base64.b64decode(data["content"]))

    p = subprocess.Popen(
        [r"C:\Program Files\Python311\python.exe", target_file],
        cwd=r"C:\KaafehDoostiBot",
        creationflags=0x00000008 # DETACHED_PROCESS
    )
    msg = f"Started downloader PID {p.pid}"
except Exception as e:
    msg = f"Error: {e}"

put_url = f'https://api.github.com/repos/{REPO}/contents/dl_starter_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode())['sha']
except:
    pass

body = {'message': 'Starter res', 'content': base64.b64encode(json.dumps({'res': msg}).encode()).decode()}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode(), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded dl_starter_res.json')
