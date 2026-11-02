# -*- coding: utf-8 -*-
import os, sys, sqlite3, json, base64, urllib.request

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
base_dir = r"C:\KaafehDoostiBot"
res["files"] = []
if os.path.exists(base_dir):
    for f in os.listdir(base_dir):
        fp = os.path.join(base_dir, f)
        res["files"].append({
            "name": f,
            "size": os.path.getsize(fp) if os.path.isfile(fp) else -1,
            "is_dir": os.path.isdir(fp)
        })

db_file = os.path.join(base_dir, "bot_database.db")
if os.path.exists(db_file):
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        res["db_tables"] = tables
        res["db_counts"] = {}
        for t in tables:
            res["db_counts"][t] = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        conn.close()
    except Exception as e:
        res["db_error"] = str(e)
else:
    res["db_missing"] = True

content_b64 = base64.b64encode(json.dumps(res, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/vps_db_audit.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Audit VPS DB and files', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded vps_db_audit.json')
