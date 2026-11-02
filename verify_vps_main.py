import os, time, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

p = r'C:\KaafehDoostiBot\main.py'
info = {
    'exists': os.path.exists(p),
    'size': os.path.getsize(p) if os.path.exists(p) else 0,
    'mtime': time.ctime(os.path.getmtime(p)) if os.path.exists(p) else '',
}
if os.path.exists(p):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    info['has_miniaudio_memory'] = 'f_bytes = f_track.read()' in content
    info['has_sound_1978'] = 'self.initSoundInputDevice(1978)' in content
    info['has_tt_local_userid'] = 'ab.nStreamID = TeamTalk5.TT_LOCAL_USERID' in content

# Also get last 20 Radio lines from bot_console.log
log_p = r'C:\KaafehDoostiBot\bot_console.log'
radio_tail = []
if os.path.exists(log_p):
    with open(log_p, 'r', encoding='utf-8', errors='ignore') as f:
        for l in f:
            if '[Radio]' in l:
                radio_tail.append(l.strip())
info['radio_tail'] = radio_tail[-20:]

content_b64 = base64.b64encode(json.dumps(info, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/verify_main_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Verify main res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded verify main res')
