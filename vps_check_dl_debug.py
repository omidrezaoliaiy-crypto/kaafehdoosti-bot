import os, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
log_f = r"C:\download_log.txt"

res = {
    "log": open(log_f, "r", encoding="utf-8", errors="ignore").read()[-2000:] if os.path.exists(log_f) else "NO_LOG_FILE"
}

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/download_debug_log.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        sha = json.loads(resp.read().decode())['sha']
except:
    pass

body = {'message': 'Download debug log', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode(), headers=headers, method='PUT')
with urllib.request.urlopen(req) as resp:
    print('Uploaded:', resp.status)
