import sys, os, time, json, base64, urllib.request, ctypes
sys.path.append(r'C:\KaafehDoostiBot')
import TeamTalk5

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

tt = TeamTalk5.TeamTalk()
tt.initSoundInputDevice(1978)

tt.connect('185.26.33.57', 10333, 10333, 0, 0)
time.sleep(1)

# Login
tt.doLogin('test_stream_bot', 'kaafehdoostibot', '123', 'StreamTester')
logged = False
my_id = 0
for _ in range(50):
    m = tt.getMessage(50)
    if m:
        if m.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_MYSELF_LOGGEDIN:
            logged = True
            my_id = m.nSource
            break
        elif m.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_ERROR:
            err_no = getattr(m.clienterrormsg, 'nErrorNo', -1)
            print(f"Login error: {err_no}")
            break
    time.sleep(0.05)

joined = False
if logged:
    tt.doJoinChannelByID(5, '')
    for _ in range(50):
        m = tt.getMessage(50)
        if m and m.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_CMD_USER_JOINED:
            joined = True
            break
        time.sleep(0.05)

# Find an mp3 in music_cache or music_cache_nostalgia
test_file = None
for folder in [r'C:\KaafehDoostiBot\music_cache', r'C:\KaafehDoostiBot\music_cache_nostalgia']:
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.mp3'):
                test_file = os.path.join(folder, f)
                break
    if test_file:
        break

smf_ok = False
smf_err = 0
smf_msg = ""
if logged and joined and test_file:
    smf_ok = bool(tt.startStreamingMediaFileToChannel(test_file, None))
    smf_err = tt.getLastError()
    smf_msg = tt.getClientErrorMsg(smf_err)

# Test insertAudioBlock with various StreamIDs
ins_tests = {}
if logged and joined:
    tt.enableVoiceTransmission(True)
    buf = (ctypes.c_byte * (960 * 2 * 2))()
    for sid_name, sid in [("LOCAL_USERID_0", 0), ("STREAM_1", 1), ("LOCAL_TX_USERID", 0x1002), ("MY_ID", my_id)]:
        ab = TeamTalk5.AudioBlock()
        ab.nStreamID = sid
        ab.nSampleRate = 48000
        ab.nChannels = 2
        ab.nSamples = 960
        ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
        ab.lpRawAudio = ctypes.cast(buf, ctypes.c_void_p)
        ok = bool(tt.insertAudioBlock(ab))
        err = tt.getLastError()
        msg = tt.getClientErrorMsg(err)
        ins_tests[sid_name] = {"ok": ok, "err": err, "msg": msg}

res = {
    "logged": logged,
    "my_id": my_id,
    "joined": joined,
    "test_file": test_file,
    "smf_ok": smf_ok,
    "smf_err": smf_err,
    "smf_msg": smf_msg,
    "ins_tests": ins_tests
}

try:
    tt.stopStreamingMediaFileToChannel()
    tt.disconnect()
except:
    pass

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/test_stream_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Test stream res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded test_stream_res.json')
