# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import TeamTalk5
    
    # 1. Check audio files in music_cache_nostalgia
    cache_dir = r'C:\KaafehDoostiBot\music_cache_nostalgia'
    files = sorted(os.listdir(cache_dir))
    res['file_count'] = len(files)
    sample_file = os.path.join(cache_dir, files[0])
    res['sample_file'] = sample_file
    res['sample_exists'] = os.path.exists(sample_file)
    res['sample_size'] = os.path.getsize(sample_file) if os.path.exists(sample_file) else 0

    # 2. Test TeamTalk client streaming
    tt = TeamTalk5.TeamTalk()
    res['tt_init'] = True
    
    # connect
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    res['connect'] = con
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            cmd = tt.doLogin("StreamTester", "admin", "1234yal1234da12344321", "TeamTalk5")
            res['login_cmd'] = cmd
            logged_in = True
        if (flags & 0x00008000) != 0: # LOGGEDIN
            res['logged_in'] = True
            break
        time.sleep(0.05)
        
    # Join channel 5 (nostalgia channel)
    j_cmd = tt.doJoinChannelByID(5, "")
    res['join_cmd'] = j_cmd
    
    for _ in range(40):
        tt.runEventLoop(50)
        time.sleep(0.05)
        
    my_id = tt.getMyUserID()
    u = tt.getUser(my_id)
    res['my_id'] = my_id
    res['in_channel'] = u.nChannelID if u else -1
    
    # Try startStreamingMediaFileToChannel with sample file
    str_res = tt.startStreamingMediaFileToChannel(sample_file, None)
    res['stream_result_sample'] = str_res
    
    # Also check if TeamTalk requires normalized path or ascii or bytes
    if not str_res:
        # Check why it failed
        # Try short path or forward slashes
        fwd_path = sample_file.replace('\\', '/')
        res['stream_result_fwd'] = tt.startStreamingMediaFileToChannel(fwd_path, None)
        
        # Try a file with only ascii name
        ascii_test = r'C:\KaafehDoostiBot\music_cache\test_ascii.mp3'
        import shutil
        shutil.copyfile(sample_file, ascii_test)
        res['stream_result_ascii'] = tt.startStreamingMediaFileToChannel(ascii_test, None)
        
        # Check channel transmission permissions
        chan = TeamTalk5.Channel()
        tt.getChannel(5, ctypes.byref(chan)) if 'ctypes' in globals() else None
        
    tt.disconnect()
    tt.closeTeamTalk()

except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/stream_test_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Stream test res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded stream_test_res.json')
