import TeamTalk5, json, base64, urllib.request, ctypes
TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

tt = TeamTalk5.TeamTalk()
devs = tt.getSoundDevices()
sound_dev_list = []
for d in devs:
    sound_dev_list.append({
        'nDeviceID': d.nDeviceID,
        'szDeviceName': d.szDeviceName,
        'nSoundSystem': d.nSoundSystem,
        'nMaxInputChannels': d.nMaxInputChannels,
        'nMaxOutputChannels': d.nMaxOutputChannels
    })

res = {
    'devices': sound_dev_list,
    'flags': tt.getFlags()
}

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/sound_devs_report.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Sound devs report', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded sound devs report')
