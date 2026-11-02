# -*- coding: utf-8 -*-
import os, json, time, urllib.request, base64

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

log_path = r'C:\KaafehDoostiBot\bot_console.log'
radio_lines = []
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for l in f:
            if 'Radio' in l or 'رادیو' in l or 'radio' in l:
                radio_lines.append(l.strip())

report = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'radio_lines_count': len(radio_lines),
    'radio_tail': radio_lines[-40:]
}

content_b64 = base64.b64encode(json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')).decode('utf-8')
url = f'https://api.github.com/repos/{REPO}/contents/radio_report.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Radio Report', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Radio report uploaded successfully!')
