import os, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

log_path = r'C:\KaafehDoostiBot\bot_console.log'
res = {}
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    res['total_lines'] = len(lines)
    radio_lines = [l.strip() for l in lines if '[Radio' in l or 'رادیو' in l]
    res['radio_lines'] = radio_lines[-40:]
    res['last_40'] = [l.strip() for l in lines[-40:]]
else:
    res['found'] = False

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/radio_log_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Radio log res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded radio_log_res.json')
