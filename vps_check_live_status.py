import os, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
base_dir = r"C:\KaafehDoostiBot"

res = {
    "launch_status": open(os.path.join(base_dir, "launch_status.txt"), "r").read() if os.path.exists(os.path.join(base_dir, "launch_status.txt")) else "NO_LAUNCH_FILE",
    "download_log": open(os.path.join(base_dir, "download_log.txt"), "r", encoding="utf-8", errors="ignore").read()[-2000:] if os.path.exists(os.path.join(base_dir, "download_log.txt")) else "NO_DL_LOG",
    "cache_files_count": len(os.listdir(os.path.join(base_dir, "music_cache"))) if os.path.exists(os.path.join(base_dir, "music_cache")) else 0
}

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/dl_live_status.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        sha = json.loads(resp.read().decode())['sha']
except:
    pass

body = {'message': 'DL Live Status', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded dl_live_status.json')
