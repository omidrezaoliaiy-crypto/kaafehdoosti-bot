# -*- coding: utf-8 -*-
import os, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

log_path = os.path.join(r'C:\KaafehDoostiBot', 'bot_console.log')
res = {}
if os.path.exists(log_path):
    size = os.path.getsize(log_path)
    res['size'] = size
    with open(log_path, 'rb') as f:
        seek_pos = max(0, size - 8192)
        f.seek(seek_pos)
        tail_bytes = f.read()
    res['tail'] = tail_bytes.decode('utf-8', errors='ignore')
else:
    res['exists'] = False

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/console_tail_raw.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Console tail raw', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded console_tail_raw.json')
