import sys, os, json, base64, urllib.request, traceback
sys.path.append(r'C:\KaafehDoostiBot')

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    import TeamTalk5
    import main
    res["import_ok"] = True
    try:
        r = main.RadioMusicBot()
        res["radio_bot_created"] = True
        res["playlist_len"] = len(r.playlist)
        res["chan_id"] = r.chan_id
        res["user"] = r.tt_user
    except Exception as e:
        res["radio_bot_created"] = False
        res["radio_err"] = str(e)
        res["radio_tb"] = traceback.format_exc()
except Exception as e:
    res["import_ok"] = False
    res["import_err"] = str(e)
    res["import_tb"] = traceback.format_exc()

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/diag_radio_res.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Diag radio res', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded diag_radio_res.json')
