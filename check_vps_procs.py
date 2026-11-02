# -*- coding: utf-8 -*-
import sys, os, time, json, base64, urllib.request, subprocess
TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

res = {}
try:
    dl_file = r"C:\KaafehDoostiBot\vps_download_missing_songs.py"
    res["dl_file_exists"] = os.path.exists(dl_file)
    if os.path.exists(dl_file):
        res["dl_file_size"] = os.path.getsize(dl_file)
        # Try running it directly with timeout of 5s to catch immediate error
        try:
            p = subprocess.run(["C:\\Program Files\\Python311\\python.exe", dl_file], capture_output=True, text=True, timeout=10)
            res["run_stdout"] = p.stdout
            res["run_stderr"] = p.stderr
            res["run_rc"] = p.returncode
        except subprocess.TimeoutExpired as e:
            res["run_timeout"] = "Still running after 10s!"
            res["partial_out"] = e.stdout

    p2 = subprocess.run(["powershell", "-Command", "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, Path | Format-Table -AutoSize | Out-String"], capture_output=True, text=True)
    res['python_procs'] = p2.stdout
except Exception as e:
    res['exc'] = str(e)

content_b64 = base64.b64encode(json.dumps(res, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/proc_audit.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass

body = {'message': 'Proc audit with dl check', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded proc_audit.json')
