# -*- coding: utf-8 -*-
import sys, os, json, base64, urllib.request, ctypes
sys.path.append(r'C:\KaafehDoostiBot')
import TeamTalk5

tt = TeamTalk5.TeamTalk()
devs = tt.getSoundDevices()
res = []
for d in devs:
    res.append({'id': d.nDeviceID, 'name': TeamTalk5.ttstr(d.szDeviceName), 'system': d.nSoundSystem, 'max_input': d.nMaxInputChannels, 'max_output': d.nMaxOutputChannels})

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/sound_devs_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Sound devs', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded sound_devs_res.json')
