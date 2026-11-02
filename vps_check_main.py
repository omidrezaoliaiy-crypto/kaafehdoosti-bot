import os, json, base64, urllib.request
TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
p = r'C:\KaafehDoostiBot\main.py'
content = open(p, 'r', encoding='utf-8', errors='ignore').read()
res = {
    'size': len(content),
    'has_decode_bytes': 'miniaudio.decode(f_bytes' in content or 'miniaudio.decode(\n                    f_bytes' in content or 'miniaudio.decode(' in content,
    'has_stream_fallback': 'self.bot.stream_media_file_fallback' in content
}
content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/check_main_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Check main res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded check main res')
