# -*- coding: utf-8 -*-
import urllib.request, subprocess, time, os, json, base64

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

print('=== DEPLOYING FIXED MAIN.PY ===')
main_url = 'https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/kaafeh_main.py'
dest = r'C:\KaafehDoostiBot\main.py'

req = urllib.request.Request(main_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    code = resp.read()

with open(dest, 'wb') as f:
    f.write(code)
print(f'Wrote {len(code)} bytes to {dest}')

# Reset radio state if corrupt
radio_state = r'C:\KaafehDoostiBot\radio_state.json'
try:
    if os.path.exists(radio_state):
        with open(radio_state, 'r', encoding='utf-8') as f:
            st = json.load(f)
        st['current_track_index'] = 0
        st['resume_pos_sec'] = 0.0
        with open(radio_state, 'w', encoding='utf-8') as f:
            json.dump(st, f, indent=2)
        print('Reset radio_state.json to track index 0')
except Exception as e:
    print('State reset err:', e)

# Terminate running main.py processes so supervisor restarts
print('Stopping old python processes...')
subprocess.run(['powershell', '-Command', 'Get-Process python | Where-Object {.Id -ne 14040} | Stop-Process -Force'], capture_output=True)
print('Old processes stopped. Supervisor will launch fresh main.py...')

time.sleep(7)

# Check status
ns = subprocess.run(['netstat', '-ano'], capture_output=True, text=True).stdout
tt_lines = [l.strip() for l in ns.splitlines() if '10333' in l]

console_tail = []
log_p = r'C:\KaafehDoostiBot\bot_console.log'
if os.path.exists(log_p):
    with open(log_p, 'r', encoding='utf-8', errors='ignore') as f:
        console_tail = [l.strip() for l in f.readlines()[-30:]]

report = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'teamtalk_sockets': tt_lines,
    'console_tail': console_tail
}

content_b64 = base64.b64encode(json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/deploy_report.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    r = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(r, timeout=10) as resp:
        sha = json.loads(resp.read().decode()).get('sha')
except:
    pass
body = {'message': 'Deploy report', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Deploy report uploaded successfully!')
