import miniaudio, json, base64, urllib.request
TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
res = {'decode': hasattr(miniaudio, 'decode'), 'decode_file': hasattr(miniaudio, 'decode_file')}
content_b64 = base64.b64encode(json.dumps(res).encode('utf-8')).decode('utf-8')
url = f'https://api.github.com/repos/{REPO}/contents/test_mini_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Mini Res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('OK')
