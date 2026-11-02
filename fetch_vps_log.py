# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    log_path = r'C:\KaafehDoostiBot\bot_console.log'
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            res['console_tail'] = lines[-60:]
            
    watchdog_log = r'C:\KaafehDoostiBot\bot_watchdog.log'
    if os.path.exists(watchdog_log):
        with open(watchdog_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            res['watchdog_tail'] = lines[-30:]
            
    res['env_ENABLE_TT_BOTS'] = os.environ.get("ENABLE_TT_BOTS")
except Exception as e:
    res['exc'] = str(e)

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/vps_log_tail.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'VPS log tail', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded vps_log_tail.json')
