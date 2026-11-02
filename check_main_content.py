# -*- coding: utf-8 -*-
import os, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

main_path = r'C:\KaafehDoostiBot\main.py'
res = {}
if os.path.exists(main_path):
    with open(main_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    res['has_direct_voice'] = 'Playing direct voice' in text
    res['has_silent_bug'] = 'silent={is_silent}' in text
    res['radio_worker_started'] = '[Radio Worker Thread] Started!' in text
    idx = text.find('def play_track')
    res['play_track_snippet'] = text[idx:idx+500] if idx != -1 else 'not found'
else:
    res['exists'] = False

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/main_content_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Main content res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded main_content_res.json')
