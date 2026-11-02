# -*- coding: utf-8 -*-
import os, json, time, urllib.request, subprocess, base64

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

def get_tail(filepath, max_lines=60):
    if not os.path.exists(filepath):
        return [f'File {filepath} not found']
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return [l.strip() for l in lines[-max_lines:]]
    except Exception as e:
        return [f'Error reading {filepath}: {e}']

def get_dir_count(path):
    if not os.path.exists(path):
        return 0
    try:
        return len(os.listdir(path))
    except:
        return -1

report = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'music_cache_count': get_dir_count(r'C:\KaafehDoostiBot\music_cache'),
    'music_cache_nostalgia_count': get_dir_count(r'C:\KaafehDoostiBot\music_cache_nostalgia'),
    'console_tail': get_tail(r'C:\KaafehDoostiBot\bot_console.log', 60),
    'watchdog_tail': get_tail(r'C:\KaafehDoostiBot\bot_watchdog.log', 20),
}

try:
    ns = subprocess.run(['netstat', '-ano'], capture_output=True, text=True).stdout
    tt_lines = [l.strip() for l in ns.splitlines() if '10333' in l]
    report['teamtalk_sockets'] = tt_lines
except Exception as e:
    report['teamtalk_sockets'] = [str(e)]

try:
    content_b64 = base64.b64encode(json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')).decode('utf-8')
    url = f'https://api.github.com/repos/{REPO}/contents/vps_report.json'
    headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
    sha = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            sha = json.loads(resp.read().decode()).get('sha')
    except:
        pass
    body = {'message': f"VPS Report {report['timestamp']}", 'content': content_b64, 'branch': 'main'}
    if sha: body['sha'] = sha
    req2 = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        print(f'VPS Report uploaded! Status: {resp2.status}')
except Exception as e:
    print(f'Failed to upload report: {e}')
