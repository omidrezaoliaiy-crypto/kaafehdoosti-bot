import sys, os, time, json, base64, urllib.request, sqlite3, traceback
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import main
    res['imported'] = True
    t0 = time.time()
    v = main.load_persistent_config("volume_percent")
    res['load_time'] = time.time() - t0
    res['vol'] = v
    
    t1 = time.time()
    r = main.RadioMusicBot()
    res['radio_init_time'] = time.time() - t1
    res['radio_playlist_len'] = len(r.playlist)
    res['radio_created'] = True
    
    t2 = time.time()
    res['connect_res'] = r.connect(main.SHARED_TT_HOST, main.SHARED_TT_PORT, main.SHARED_TT_PORT, 0, 0, False)
    res['connect_time'] = time.time() - t2
    
    # Run loop for 2 seconds to see if it logs in
    for _ in range(40):
        r.runEventLoop(50)
        if getattr(r, 'logged_in', False):
            res['logged_in'] = True
            res['my_id'] = r.my_user_id
            break
        time.sleep(0.05)
        
    res['connected_flag'] = r.connected
    res['flags'] = r.getFlags()
    res['diag'] = r.diag
    r.disconnect()
except Exception as e:
    res['err'] = str(e)
    res['tb'] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/test_load_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Test load res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded test_load_res.json')
