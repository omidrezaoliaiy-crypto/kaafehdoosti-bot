import sys, os, time, json, base64, urllib.request, traceback
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import TeamTalk5
    import main
    bot = main.RadioMusicBot()
    res["created"] = True
    con = bot.connect(main.SHARED_TT_HOST, main.SHARED_TT_PORT, main.SHARED_TT_PORT, 0, 0, False)
    res["con_res"] = con
    for _ in range(40):
        m = bot.getMessage(50)
        if m:
            event = m.nClientEvent
            bot.runEventLoop(50)
            if getattr(bot, "logged_in", False):
                res["logged_in"] = True
                res["my_id"] = bot.my_user_id
                res["chan_id"] = bot.chan_id
                res["joined"] = bot.joined
                break
        time.sleep(0.05)
    res["connected"] = bot.connected
    res["flags"] = bot.getFlags()
    res["diag"] = bot.diag
    bot.disconnect()
except Exception as e:
    res["error"] = str(e)
    res["tb"] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/test_radio_con_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Test radio con res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded test_radio_con_res.json')
