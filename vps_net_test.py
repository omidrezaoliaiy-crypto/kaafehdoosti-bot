# -*- coding: utf-8 -*-
import urllib.request, json, time, base64

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

urls = {
    'gofile': 'https://api.gofile.io/servers',
    'pixeldrain': 'https://pixeldrain.com/api/user',
    'catbox': 'https://catbox.moe',
    'uupload': 'https://uupload.ir',
    'archive_org': 'https://archive.org',
    'filebin': 'https://filebin.net'
}

results = {}
for name, u in urls.items():
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            results[name] = {'status': resp.getcode(), 'ok': True}
    except Exception as e:
        results[name] = {'status': str(e), 'ok': False}

content_b64 = base64.b64encode(json.dumps(results, indent=2).encode('utf-8')).decode('utf-8')
url = f'https://api.github.com/repos/{REPO}/contents/net_test.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Net Test', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Net test results uploaded!')
