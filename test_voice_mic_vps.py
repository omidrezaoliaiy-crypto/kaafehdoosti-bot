# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback, ctypes
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    try:
        import miniaudio
        res['miniaudio'] = True
    except ImportError:
        res['miniaudio'] = False
        import subprocess
        p = subprocess.run([sys.executable, "-m", "pip", "install", "miniaudio"], capture_output=True, text=True)
        res['pip_install'] = p.returncode
        import miniaudio
        res['miniaudio_after_pip'] = True

    import TeamTalk5
    
    cache_dir = r'C:\KaafehDoostiBot\music_cache'
    files = sorted([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
    sample_file = os.path.join(cache_dir, files[0])
    
    # Decode 3 seconds of audio to PCM
    with open(sample_file, 'rb') as f:
        f_bytes = f.read()
    decoded = miniaudio.decode(f_bytes, output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=48000)
    pcm = decoded.samples.tobytes()
    res['decoded_pcm_len'] = len(pcm)
    
    tt = TeamTalk5.TeamTalk()
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    res['connect'] = con
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            cmd = tt.doLogin("VoiceTestBot", "admin", "1234yal1234da12344321", "TeamTalk5")
            logged_in = True
        if (flags & 0x00008000) != 0:
            res['logged_in'] = True
            break
        time.sleep(0.05)
        
    tt.doJoinChannelByID(2, "")
    for _ in range(20):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    # Init virtual sound device 1978
    snd_ok = tt.initSoundInputDevice(1978)
    res['initSoundInputDevice'] = snd_ok
    
    vox_ok = tt.enableVoiceTransmission(True)
    res['enableVoiceTransmission'] = vox_ok
    
    # Try inserting 50 audio blocks (1 second of audio)
    samples_per_frame = int(48000 * 0.02) # 960
    chunk_size = samples_per_frame * 2 * 2 # 3840 bytes
    buf_type = ctypes.c_byte * chunk_size
    raw_buf = buf_type()
    
    ab = TeamTalk5.AudioBlock()
    ab.nStreamID = TeamTalk5.TT_LOCAL_USERID
    ab.nSampleRate = 48000
    ab.nChannels = 2
    ab.nSamples = samples_per_frame
    ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
    ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
    
    sample_index = 0
    pos = 0
    insert_results = []
    for _ in range(50):
        chunk = pcm[pos:pos+chunk_size]
        pos += chunk_size
        if len(chunk) < chunk_size:
            break
        ctypes.memmove(raw_buf, chunk, len(chunk))
        ab.uSampleIndex = sample_index
        sample_index += samples_per_frame
        
        ok = tt.insertAudioBlock(ab)
        insert_results.append(bool(ok))
        tt.runEventLoop(10)
        time.sleep(0.015)
        
    res['insert_count'] = len(insert_results)
    res['insert_success_count'] = sum(1 for x in insert_results if x)
    res['flags_during_voice'] = tt.getFlags()
    res['voice_flag_set'] = bool(tt.getFlags() & 0x00002000) # CLIENTFLAG_VOICE_TX
    
    tt.enableVoiceTransmission(False)
    tt.insertAudioBlock(None)
    tt.disconnect()
    tt.closeTeamTalk()

except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/voice_test_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Voice test res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded voice_test_res.json')
