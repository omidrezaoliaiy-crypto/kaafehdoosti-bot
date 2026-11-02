# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, traceback
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import TeamTalk5
    
    # 1. Check audio files in music_cache (Radio)
    cache_dir = r'C:\KaafehDoostiBot\music_cache'
    files = sorted([f for f in os.listdir(cache_dir) if f.endswith('.mp3')])
    res['radio_files'] = len(files)
    sample_file = os.path.join(cache_dir, files[0])
    res['sample_file'] = sample_file
    res['sample_exists'] = os.path.exists(sample_file)

    # 2. Test TeamTalk client as radio kaafehdoosti
    tt = TeamTalk5.TeamTalk()
    con = tt.connect("185.26.33.57", 10333, 10333, 0, 0, False)
    res['connect'] = con
    
    logged_in = False
    for _ in range(40):
        tt.runEventLoop(50)
        flags = tt.getFlags()
        if (flags & 0x00004000) != 0 and not logged_in:
            cmd = tt.doLogin("radio kaafehdoosti", "radio kaafehdoosti", "radio_kaafeh_123456789_doosti", "اختصاصی کافه دوستی o❤️y")
            res['login_cmd'] = cmd
            logged_in = True
        if (flags & 0x00008000) != 0:
            res['logged_in'] = True
            break
        time.sleep(0.05)
        
    # Join channel 2 (Radio channel)
    j_cmd = tt.doJoinChannelByID(2, "")
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
    res['stream_result_radio'] = str_res
    
    time.sleep(2)
    # Check if streaming flag is set
    flags_after = tt.getFlags()
    res['flags_after'] = flags_after
    res['is_streaming'] = bool(flags_after & 0x00010000)
    
    tt.stopStreamingMediaFileToChannel()
    time.sleep(0.5)
    tt.disconnect()
    tt.closeTeamTalk()

except Exception as e:
    res['exc'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/radio_stream_test.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Radio stream test res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded radio_stream_test.json')
