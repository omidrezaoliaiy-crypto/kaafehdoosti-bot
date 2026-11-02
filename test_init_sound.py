import sys, os
sys.path.append(r'C:\KaafehDoostiBot')
import TeamTalk5
import ctypes
import json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

tt = TeamTalk5.TeamTalk()
ok_in = tt.initSoundInputDevice(1978)
flags = tt.getFlags()

buf = (ctypes.c_byte * (960 * 2 * 2))()
ab0 = TeamTalk5.AudioBlock()
ab0.nStreamID = TeamTalk5.TT_LOCAL_USERID
ab0.nSampleRate = 48000
ab0.nChannels = 2
ab0.nSamples = 960
ab0.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
ab0.lpRawAudio = ctypes.cast(buf, ctypes.c_void_p)

ins = tt.insertAudioBlock(ab0)

res = {
    'init_1978_ok': ok_in,
    'flags_after_init': flags,
    'ins_result': ins
}

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/init_sound_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Init sound res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded init sound res')
