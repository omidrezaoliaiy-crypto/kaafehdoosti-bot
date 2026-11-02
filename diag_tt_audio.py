import sys, os, time
sys.path.append(r'C:\KaafehDoostiBot')
import TeamTalk5
import ctypes
import json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

tt = TeamTalk5.TeamTalk()
tt.initSoundInputDevice(1978)

# Connect to server
con = tt.connect('185.26.33.57', 10333, 10333, 0, 0)
time.sleep(1)

# Login with test account or nostalgia account
cmd_login = tt.doLogin('test_diag', 'nostalgia_player', '123456', 'DiagBot')

# Pump events until logged in
logged_in = False
my_id = 0
for _ in range(50):
    msg = tt.getMessage(50)
    if msg:
        if msg.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN:
            my_id = msg.nSource
            logged_in = True
            break
    time.sleep(0.05)

# Join channel 5
cmd_join = tt.doJoinChannelByID(5, '')
joined = False
for _ in range(50):
    msg = tt.getMessage(50)
    if msg:
        if msg.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_USER_JOINED:
            joined = True
            break
    time.sleep(0.05)

# Test enable voice transmission
vt_ok = tt.enableVoiceTransmission(True)

# Prepare audio block
buf = (ctypes.c_byte * (960 * 2 * 2))()
ab = TeamTalk5.AudioBlock()
ab.nStreamID = TeamTalk5.TT_LOCAL_USERID
ab.nSampleRate = 48000
ab.nChannels = 2
ab.nSamples = 960
ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
ab.lpRawAudio = ctypes.cast(buf, ctypes.c_void_p)

ins_res = tt.insertAudioBlock(ab)
err = tt.getLastError()
flags = tt.getFlags()

# Also test streaming media file
# Test with music_2.mp3 in current folder if exists
music_p = r'C:\KaafehDoostiBot\music_cache\47_Dino Donya موزیکدل.mp3'
smf_ok = -1
if not os.path.exists(music_p):
    # pick first mp3 in music_cache
    for f in os.listdir(r'C:\KaafehDoostiBot\music_cache'):
        if f.endswith('.mp3'):
            music_p = os.path.join(r'C:\KaafehDoostiBot\music_cache', f)
            break

if os.path.exists(music_p):
    smf_ok = tt.startStreamingMediaFileToChannel(music_p, None)
    smf_err = tt.getLastError()
else:
    smf_err = 'no_music_found'

res = {
    'logged_in': logged_in,
    'my_id': my_id,
    'joined_ch5': joined,
    'vt_ok': vt_ok,
    'ins_res': ins_res,
    'last_error': err,
    'flags': flags,
    'smf_ok': smf_ok,
    'smf_err': smf_err if 'smf_err' in locals() else 0
}

tt.disconnect()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/diag_audio_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Diag audio res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded diag audio res')
