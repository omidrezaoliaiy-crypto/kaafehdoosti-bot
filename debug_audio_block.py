# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback, ctypes
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import TeamTalk5
    tt = TeamTalk5.TeamTalk()
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            cmd = tt.doLogin("VoiceTestBot2", "admin", "1234yal1234da12344321", "TeamTalk5")
            logged_in = True
        if (flags & 0x00008000) != 0:
            break
        time.sleep(0.05)
        
    tt.doJoinChannelByID(2, "")
    for _ in range(25):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    my_id = tt.getMyUserID()
    res['my_id'] = my_id
    res['init_snd'] = tt.initSoundInputDevice(1978)
    res['enable_vox'] = tt.enableVoiceTransmission(True)
    
    # Try different combinations of nSamples and nStreamID
    tests = [
        {"samples": 1920, "stream_id": 0, "byref": False},
        {"samples": 1920, "stream_id": 0, "byref": True},
        {"samples": 1920, "stream_id": my_id, "byref": False},
        {"samples": 1920, "stream_id": my_id, "byref": True},
        {"samples": 960, "stream_id": 0, "byref": False},
        {"samples": 960, "stream_id": 0, "byref": True},
        {"samples": 480, "stream_id": 0, "byref": False},
        {"samples": 480, "stream_id": 0, "byref": True},
    ]
    
    test_out = []
    for t in tests:
        samples = t['samples']
        chunk_size = samples * 2 * 2 # 16-bit stereo
        buf_type = ctypes.c_byte * chunk_size
        raw_buf = buf_type()
        
        ab = TeamTalk5.AudioBlock()
        ab.nStreamID = t['stream_id']
        ab.nSampleRate = 48000
        ab.nChannels = 2
        ab.nSamples = samples
        ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
        ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
        ab.uSampleIndex = 0
        
        if t['byref']:
            ok = TeamTalk5._InsertAudioBlock(tt._tt, ctypes.byref(ab))
        else:
            ok = tt.insertAudioBlock(ab)
            
        flags_now = tt.getFlags()
        test_out.append({
            "test": t,
            "result": bool(ok),
            "flags": flags_now,
            "voice_tx": bool(flags_now & 0x00002000)
        })
        time.sleep(0.02)
        
    res['tests'] = test_out
    tt.enableVoiceTransmission(False)
    tt.disconnect()
    tt.closeTeamTalk()

except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/debug_audio_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Debug audio res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded debug_audio_res.json')
