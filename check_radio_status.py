import sys, os
import json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

log_file = r'C:\KaafehDoostiBot\bot_console.log'
radio_lines = []
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '[Radio]' in line:
                radio_lines.append(line.strip())

res = {
    'count': len(radio_lines),
    'tail': radio_lines[-30:]
}

content_b64 = base64.b64encode(json.dumps(res, ensure_ascii=False, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/radio_status.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Radio status', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded radio status')
