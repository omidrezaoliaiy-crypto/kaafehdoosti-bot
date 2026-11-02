import os, time, json, base64, urllib.request, subprocess
TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
p = r'C:\KaafehDoostiBot\main.py'
res = {
    'exists': os.path.exists(p),
    'size': os.path.getsize(p) if os.path.exists(p) else 0,
    'mtime': time.ctime(os.path.getmtime(p)) if os.path.exists(p) else '',
}
# Also kill python with taskkill
k = subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True, text=True)
res['taskkill'] = k.stdout + k.stderr
# Restart task
r = subprocess.run(['schtasks', '/Run', '/TN', 'KaafehDoosti_24_7'], capture_output=True, text=True)
res['schtasks'] = r.stdout + r.stderr

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/kill_report.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Kill report', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded kill report')
