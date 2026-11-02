# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback, ctypes, audioop, threading
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}

class VoicePlayerTest:
    def __init__(self, tt_instance):
        self.tt = tt_instance
        self.is_playing = False
        self.stop_event = threading.Event()
        self.playback_thread = None
        self.volume_percent = 100
        self.current_sec = 0.0
        self.stream_id = 1
        
        # Audio block buffer: 1920 samples (40ms @ 48kHz stereo)
        self.samples_per_frame = 1920
        self.chunk_bytes = self.samples_per_frame * 2 * 2 # 7680 bytes
        self.buf_type = ctypes.c_byte * self.chunk_bytes
        self.raw_buf = self.buf_type()
        
        self.ab = TeamTalk5.AudioBlock()
        self.ab.nStreamID = self.stream_id
        self.ab.nSampleRate = 48000
        self.ab.nChannels = 2
        self.ab.nSamples = self.samples_per_frame
        self.ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
        self.ab.lpRawAudio = ctypes.cast(self.raw_buf, ctypes.c_void_p)
        self.ab.uSampleIndex = 0

    def play_file(self, file_path, start_sec=0.0):
        self.stop()
        import miniaudio
        t0 = time.time()
        with open(file_path, 'rb') as f:
            f_bytes = f.read()
        decoded = miniaudio.decode(f_bytes, output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=48000)
        pcm = decoded.samples.tobytes()
        decode_time = time.time() - t0
        
        self.stream_id += 1
        self.ab.nStreamID = self.stream_id
        self.stop_event.clear()
        self.is_playing = True
        
        self.playback_thread = threading.Thread(
            target=self._play_loop,
            args=(pcm, start_sec, decode_time),
            daemon=True
        )
        self.playback_thread.start()

    def _play_loop(self, pcm, start_sec, decode_time):
        bytes_per_sec = 48000 * 2 * 2 # 192,000 bytes/sec
        start_pos = int(start_sec * bytes_per_sec)
        # Align to frame size
        start_pos = (start_pos // self.chunk_bytes) * self.chunk_bytes
        pos = start_pos
        total_len = len(pcm)
        
        frame_duration = self.samples_per_frame / 48000.0 # 0.040s
        next_frame_time = time.time()
        
        frames_sent = 0
        while self.is_playing and not self.stop_event.is_set():
            if pos >= total_len:
                break
            chunk = pcm[pos:pos+self.chunk_bytes]
            pos += len(chunk)
            
            if len(chunk) < self.chunk_bytes:
                chunk += b'\x00' * (self.chunk_bytes - len(chunk))
                
            vol = self.volume_percent
            if vol != 100:
                factor = max(0.0, min(1.5, vol / 100.0))
                chunk = audioop.mul(chunk, 2, factor)
                
            ctypes.memmove(self.raw_buf, chunk, self.chunk_bytes)
            self.tt.insertAudioBlock(self.ab)
            frames_sent += 1
            self.current_sec = pos / bytes_per_sec
            
            next_frame_time += frame_duration
            sleep_sec = next_frame_time - time.time()
            if sleep_sec > 0.001:
                time.sleep(sleep_sec)
            elif sleep_sec < -0.1: # Clock drift reset
                next_frame_time = time.time()
                
        # End audio stream
        self.tt.insertAudioBlock(None)
        self.is_playing = False

    def stop(self):
        self.stop_event.set()
        self.is_playing = False
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
        try:
            self.tt.insertAudioBlock(None)
        except Exception:
            pass

    def set_volume(self, percent):
        self.volume_percent = percent

try:
    import miniaudio
    import TeamTalk5
    
    cache_dir = r'C:\KaafehDoostiBot\music_cache'
    files = sorted([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
    if len(files) < 2:
        raise Exception("Need at least 2 files in music_cache")
        
    track1 = os.path.join(cache_dir, files[0])
    track2 = os.path.join(cache_dir, files[1])
    
    tt = TeamTalk5.TeamTalk()
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    res['connected'] = con
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            tt.doLogin("VoiceEngineTest", "admin", "1234yal1234da12344321", "TeamTalk5")
            logged_in = True
        if (flags & 0x00008000) != 0:
            res['logged_in'] = True
            break
        time.sleep(0.05)
        
    tt.doJoinChannelByID(28, "12123123")
    for _ in range(30):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    res['channel_id'] = tt.getMyChannelID()
    
    player = VoicePlayerTest(tt)
    
    # Test 1: Play track 1 for 4 seconds at 100% volume
    t_start = time.time()
    player.play_file(track1, start_sec=0.0)
    for _ in range(40):
        tt.runEventLoop(50)
        time.sleep(0.1)
    res['track1_playing_sec'] = player.current_sec
    res['track1_is_playing'] = player.is_playing
    
    # Test 2: Adjust volume to 60% and continue for 3 seconds
    player.set_volume(60)
    for _ in range(30):
        tt.runEventLoop(50)
        time.sleep(0.1)
    res['track1_after_vol_sec'] = player.current_sec
    
    # Test 3: Stop track 1
    player.stop()
    res['stopped_ok'] = not player.is_playing
    
    # Test 4: Switch to track 2 smoothly and play for 4 seconds
    player.play_file(track2, start_sec=10.0) # Start from 10s
    for _ in range(40):
        tt.runEventLoop(50)
        time.sleep(0.1)
    res['track2_playing_sec'] = player.current_sec
    res['track2_is_playing'] = player.is_playing
    
    player.stop()
    tt.disconnect()
    res['all_tests_passed'] = True

except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/voice_engine_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Voice engine res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded voice_engine_res.json')
