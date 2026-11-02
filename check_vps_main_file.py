import sys, time, json, base64, urllib.request, py_compile
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
MAIN_DEST = r'C:\KaafehDoostiBot\main.py'
import os
if os.path.exists(MAIN_DEST):
    res['size'] = os.path.getsize(MAIN_DEST)
    try:
        py_compile.compile(MAIN_DEST, doraise=True)
        res['compile_ok'] = True
    except Exception as e:
        res['compile_ok'] = False
        res['compile_err'] = str(e)
    
    with open(MAIN_DEST, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        res['total_lines'] = len(lines)
        res['bottom_30'] = [l.strip() for l in lines[-30:]]
else:
    res['exists'] = False

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/check_main_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Check main res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded check_main_res.json')
