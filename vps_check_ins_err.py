import sys, os, time
sys.path.append(r'C:\KaafehDoostiBot')
import TeamTalk5
import ctypes
import json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

tt = TeamTalk5.TeamTalk()
tt.initSoundInputDevice(1978)
tt.connect('185.26.33.57', 10333, 10333, 0, 0)
time.sleep(1)

tt.doLogin('nostalgia player', 'nostalgia player', 'nostalgia_kaafeh_123456789_doosti', 'Test')
logged = False
for _ in range(40):
    m = tt.getMessage(50)
    if m and m.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN:
        logged = True
        break
    time.sleep(0.05)

tt.doJoinChannelByID(5, '')
joined = False
for _ in range(40):
    m = tt.getMessage(50)
    if m and m.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_USER_JOINED:
        joined = True
        break
    time.sleep(0.05)

tt.enableVoiceTransmission(True)

buf = (ctypes.c_byte * (960 * 2 * 2))()
ab = TeamTalk5.AudioBlock()
ab.nStreamID = TeamTalk5.TT_LOCAL_USERID
ab.nSampleRate = 48000
ab.nChannels = 2
ab.nSamples = 960
ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
ab.lpRawAudio = ctypes.cast(buf, ctypes.c_void_p)

ok = tt.insertAudioBlock(ab)
err = tt.getLastError()
flags = tt.getFlags()

res = {
    'logged': logged,
    'joined': joined,
    'insert_ok': ok,
    'last_err': err,
    'flags': flags
}
tt.disconnect()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/ins_err_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Ins err res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded ins err res')
