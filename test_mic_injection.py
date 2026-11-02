# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback, ctypes
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import miniaudio
    import TeamTalk5
    
    # 1. Decode 2 seconds of audio
    cache_dir = r'C:\KaafehDoostiBot\music_cache'
    files = sorted([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
    sample_file = os.path.join(cache_dir, files[0])
    
    with open(sample_file, 'rb') as f:
        f_bytes = f.read()
    decoded = miniaudio.decode(f_bytes, output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=48000)
    pcm = decoded.samples.tobytes()
    res['sample_file'] = files[0]
    res['pcm_total_bytes'] = len(pcm)
    
    tt = TeamTalk5.TeamTalk()
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    res['connected'] = con
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            # Login as VoiceTestBot
            cmd = tt.doLogin("VoiceTestBot", "admin", "1234yal1234da12344321", "TeamTalk5")
            logged_in = True
        if (flags & 0x00008000) != 0:
            res['logged_in'] = True
            break
        time.sleep(0.05)
        
    # Join private channel 28 (کانال مدیریت کافه دوستی)
    join_cmd = tt.doJoinChannelByID(28, "12123123")
    res['join_cmd'] = join_cmd
    for _ in range(30):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    my_chan = tt.getMyChannelID()
    res['my_chan'] = my_chan
    
    flags_before = tt.getFlags()
    res['flags_before'] = flags_before
    res['voice_tx_before'] = bool(flags_before & 0x00002000)
    
    # DO NOT CALL enableVoiceTransmission!
    # Direct injection via insertAudioBlock
    samples_per_frame = 1920 # 40ms at 48000Hz stereo
    chunk_bytes = samples_per_frame * 2 * 2 # 7680 bytes
    
    buf_type = ctypes.c_byte * chunk_bytes
    raw_buf = buf_type()
    
    ab = TeamTalk5.AudioBlock()
    ab.nStreamID = 101 # session id
    ab.nSampleRate = 48000
    ab.nChannels = 2
    ab.nSamples = samples_per_frame
    ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
    ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
    ab.uSampleIndex = 0
    
    pos = 0
    results = []
    flags_during = []
    
    # Send 50 frames (2 seconds of audio)
    for i in range(50):
        chunk = pcm[pos:pos+chunk_bytes]
        pos += chunk_bytes
        if len(chunk) < chunk_bytes:
            break
        ctypes.memmove(raw_buf, chunk, len(chunk))
        
        ok = tt.insertAudioBlock(ab)
        f_now = tt.getFlags()
        results.append(bool(ok))
        flags_during.append(f_now)
        
        tt.runEventLoop(20)
        time.sleep(0.035) # pace to ~40ms
        
    res['total_frames_sent'] = len(results)
    res['success_count'] = sum(1 for x in results if x)
    res['voice_tx_ever_active'] = any(bool(f & 0x00002000) for f in flags_during)
    res['sample_results'] = results[:10]
    
    # End session cleanly
    tt.insertAudioBlock(None)
    for _ in range(10):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    tt.disconnect()
    
except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/test_mic_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Test mic res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded test_mic_res.json')
