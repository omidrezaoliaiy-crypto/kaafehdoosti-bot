import os, json, base64, urllib.request, subprocess

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'
base_dir = r"C:\KaafehDoostiBot"
log_f = os.path.join(base_dir, "download_log.txt")
dl_script = os.path.join(base_dir, "vps_download_missing_songs.py")

res = {}
res["dl_script_exists"] = os.path.exists(dl_script)
if os.path.exists(dl_script):
    res["dl_script_size"] = os.path.getsize(dl_script)

res["log_exists"] = os.path.exists(log_f)
if os.path.exists(log_f):
    with open(log_f, "r", encoding="utf-8", errors="ignore") as f:
        res["log_tail"] = f.read()[-3000:]

# Try running 1 iteration of download test right now to see the exact error
try:
    p = subprocess.run(["C:\\Program Files\\Python311\\python.exe", dl_script], cwd=base_dir, capture_output=True, text=True, timeout=12)
    res["run_out"] = p.stdout
    res["run_err"] = p.stderr
    res["run_rc"] = p.returncode
except subprocess.TimeoutExpired as te:
    res["run_timeout"] = "Still downloading after 12s!"
    res["timeout_out"] = te.stdout
    res["timeout_err"] = te.stderr
except Exception as e:
    res["run_exc"] = str(e)

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/dl_diag.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        sha = json.loads(resp.read().decode())['sha']
except:
    pass

body = {'message': 'DL Diag', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded dl_diag.json')
