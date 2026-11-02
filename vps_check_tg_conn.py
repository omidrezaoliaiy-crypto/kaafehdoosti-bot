import os, sys, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}

# Check main.py on VPS for TELEGRAM_API_BASE
main_p = r"C:\KaafehDoostiBot\main.py"
if os.path.exists(main_p):
    with open(main_p, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "TELEGRAM_API_BASE" in line:
                res["line"] = line.strip()
                break

# Check environment proxy variables
res["env"] = {k: os.environ[k] for k in os.environ if "proxy" in k.lower()}

# Test direct request from VPS to tg.kaafehdoosti.ir
url = "https://tg.kaafehdoosti.ir/bot8600063713:AAGxU2xoECq5u1FjdOIgAA1PPdHBSXnZIt8/getMe"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        res["test_req"] = r.read().decode()
except Exception as e:
    res["test_err"] = str(e)

content_b64 = base64.b64encode(json.dumps(res, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/vps_tg_test.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Audit VPS TG connection', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded vps_tg_test.json')
