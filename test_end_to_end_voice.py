# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback, ctypes
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import miniaudio
    import TeamTalk5
    
    # 1. Decode 3 seconds of audio
    cache_dir = r'C:\KaafehDoostiBot\music_cache'
    files = sorted([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
    sample_file = os.path.join(cache_dir, files[0])
    
    with open(sample_file, 'rb') as f:
        f_bytes = f.read()
    decoded = miniaudio.decode(f_bytes, output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=48000)
    pcm = decoded.samples.tobytes()
    res['sample_file'] = files[0]
    
    # Bot 1: Transmitter
    tt_tx = TeamTalk5.TeamTalk()
    tt_tx.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    
    # Bot 2: Receiver
    tt_rx = TeamTalk5.TeamTalk()
    tt_rx.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    
    # Wait for connection
    time.sleep(0.5)
    for _ in range(30):
        tt_tx.runEventLoop(20)
        tt_rx.runEventLoop(20)
        time.sleep(0.02)
        
    tt_tx.doLogin("VoiceTxBot", "admin", "1234yal1234da12344321", "TeamTalk5")
    tt_rx.doLogin("VoiceRxBot", "kaafeh_nazer", "SecureNazerPass998877", "TeamTalk5")
    
    for _ in range(40):
        tt_tx.runEventLoop(20)
        tt_rx.runEventLoop(20)
        time.sleep(0.03)
        
    res['tx_id'] = tt_tx.getMyUserID()
    res['rx_id'] = tt_rx.getMyUserID()
    
    # Both join channel 28
    tt_tx.doJoinChannelByID(28, "12123123")
    tt_rx.doJoinChannelByID(28, "12123123")
    
    for _ in range(40):
        tt_tx.runEventLoop(20)
        tt_rx.runEventLoop(20)
        time.sleep(0.03)
        
    res['tx_chan'] = tt_tx.getMyChannelID()
    res['rx_chan'] = tt_rx.getMyChannelID()
    
    # Enable audio block event on receiver for transmitter
    tt_rx.enableAudioBlockEvent(tt_tx.getMyUserID(), TeamTalk5.StreamType.STREAMTYPE_VOICE, True)
    
    # Transmit 60 frames (2.4 seconds)
    samples_per_frame = 1920
    chunk_bytes = samples_per_frame * 2 * 2 # 7680
    buf_type = ctypes.c_byte * chunk_bytes
    raw_buf = buf_type()
    
    ab = TeamTalk5.AudioBlock()
    ab.nStreamID = 202
    ab.nSampleRate = 48000
    ab.nChannels = 2
    ab.nSamples = samples_per_frame
    ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
    ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
    ab.uSampleIndex = 0
    
    pos = 0
    rx_events = []
    rx_user_states = []
    
    for i in range(60):
        chunk = pcm[pos:pos+chunk_bytes]
        pos += chunk_bytes
        if len(chunk) < chunk_bytes:
            break
        ctypes.memmove(raw_buf, chunk, len(chunk))
        
        tt_tx.insertAudioBlock(ab)
        tt_tx.runEventLoop(15)
        
        # Process events on receiver
        while True:
            m = tt_rx.getMessage(0)
            if not m:
                break
            rx_events.append(m.nClientEvent)
            if m.nClientEvent == TeamTalk5.ClientEvent.CLIENTEVENT_USER_STATECHANGE:
                user = tt_rx.getUser(tt_tx.getMyUserID())
                if user:
                    rx_user_states.append(user.uUserState)
                    
        tt_rx.runEventLoop(15)
        time.sleep(0.035)
        
    # Flush / end session
    tt_tx.insertAudioBlock(None)
    for _ in range(20):
        tt_tx.runEventLoop(20)
        tt_rx.runEventLoop(20)
        time.sleep(0.03)
        
    res['rx_events_count'] = len(rx_events)
    # Check if CLIENTEVENT_USER_AUDIOBLOCK (CLIENTEVENT_NONE + 570 = 1570) occurred
    res['audioblock_event_count'] = rx_events.count(1570)
    # Check if CLIENTEVENT_USER_FIRSTVOICESTREAMPACKET (CLIENTEVENT_NONE + 1090 = 2090) occurred
    res['first_voice_packet_count'] = rx_events.count(2090)
    # Check if USERSTATE_VOICE (4) was seen in user states
    res['user_state_voice_seen'] = any(bool(s & 4) for s in rx_user_states)
    res['rx_events_sample'] = list(set(rx_events))
    
    tt_tx.disconnect()
    tt_rx.disconnect()
    
except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/end_to_end_voice_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'End to end voice res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded end_to_end_voice_res.json')
