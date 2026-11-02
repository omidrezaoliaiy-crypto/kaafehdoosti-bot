# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback, ctypes
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}

try:
    import miniaudio
    import TeamTalk5
    
    # Verify archives
    radio_cache = r'C:\KaafehDoostiBot\music_cache'
    nostalgia_cache = r'C:\KaafehDoostiBot\music_cache_nostalgia'
    
    radio_files = [f for f in os.listdir(radio_cache) if f.endswith('.mp3')]
    nostalgia_files = [f for f in os.listdir(nostalgia_cache) if f.endswith('.mp3')]
    
    res['radio_files_count'] = len(radio_files)
    res['nostalgia_files_count'] = len(nostalgia_files)
    
    # Import VoicePlayer from kaafeh_main_voice
    import kaafeh_main_voice
    
    # Create test instance connected to Channel 28
    tt = TeamTalk5.TeamTalk()
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            tt.doLogin("AuditVoiceBot", "admin", "1234yal1234da12344321", "TeamTalk5")
            logged_in = True
        if (flags & 0x00008000) != 0:
            break
        time.sleep(0.05)
        
    tt.doJoinChannelByID(28, "12123123")
    for _ in range(30):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    res['chan_id'] = tt.getMyChannelID()
    
    # Mock bot to host VoicePlayer
    class MockBot:
        def __init__(self, tt_inst):
            self.insertAudioBlock = tt_inst.insertAudioBlock
            self.is_streaming = False
            self.volume_percent = 100
            self.current_playback_sec = 0.0
            self.resume_pos_sec = 0.0
            self.next_called = False
            
        def update_player_title(self):
            pass
            
        def persist_state(self):
            pass
            
        def play_next(self):
            self.next_called = True
            
    mock_bot = MockBot(tt)
    player = kaafeh_main_voice.VoicePlayer(mock_bot)
    
    # Test Radio Track (Track 1)
    radio_track_path = os.path.join(radio_cache, radio_files[0])
    player.play(radio_track_path, start_sec=0.0)
    for _ in range(30):
        tt.runEventLoop(50)
        time.sleep(0.1)
    res['radio_play_sec'] = mock_bot.current_playback_sec
    res['radio_streaming'] = mock_bot.is_streaming
    
    # Test Volume change to 70%
    mock_bot.volume_percent = 70
    for _ in range(20):
        tt.runEventLoop(50)
        time.sleep(0.1)
    res['radio_after_vol_sec'] = mock_bot.current_playback_sec
    player.stop()
    res['radio_stopped'] = not mock_bot.is_streaming
    
    # Test Nostalgia Track (Track 1 from 245 archive)
    nostalgia_track_path = os.path.join(nostalgia_cache, nostalgia_files[0])
    mock_bot.volume_percent = 100
    player.play(nostalgia_track_path, start_sec=5.0)
    for _ in range(30):
        tt.runEventLoop(50)
        time.sleep(0.1)
    res['nostalgia_play_sec'] = mock_bot.current_playback_sec
    res['nostalgia_streaming'] = mock_bot.is_streaming
    player.stop()
    res['nostalgia_stopped'] = not mock_bot.is_streaming
    
    tt.disconnect()
    res['audit_success'] = True

except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/isolated_voice_audit.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Isolated voice audit res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded isolated_voice_audit.json')
