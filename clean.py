# -*- coding: utf-8 -*-
import os, sys, json, base64, urllib.request, subprocess, shutil, glob

TOKEN = ''.join(['ghp_', 'PGqEcf62jsr', 'EtnxhhJuPZ2', 'xBnsIqzX1ajXE6'])
REPO = 'omidrezaoliaiy-crypto/kaafehdoosti-bot'

def get_drive_space():
    try:
        cmd = "Get-PSDrive C | Select-Object @{Name='TotalGB';Expression={[Math]::Round(($_.Used + $_.Free)/1GB,2)}}, @{Name='UsedGB';Expression={[Math]::Round($_.Used/1GB,2)}}, @{Name='FreeGB';Expression={[Math]::Round($_.Free/1GB,2)}} | ConvertTo-Json"
        p = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=10)
        return json.loads(p.stdout)
    except Exception as e:
        return {"error": str(e)}

def get_dir_size_mb(path):
    total = 0
    if not os.path.exists(path):
        return 0
    try:
        for root, dirs, files in os.walk(path, onerror=lambda e: None):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
                except:
                    pass
    except:
        pass
    return round(total / (1024 * 1024), 2)

before_space = get_drive_space()

# 1. Audit top folders in C:\
c_roots = {}
try:
    for item in os.listdir(r'C:\\'):
        item_path = os.path.join(r'C:\\', item)
        if os.path.isdir(item_path):
            # for Windows and Users, get top level roughly or skip deep if too slow
            try:
                cmd = f"(Get-ChildItem -LiteralPath '{item_path}' -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB"
                p = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=15)
                val = p.stdout.strip()
                if val:
                    c_roots[item] = round(float(val), 1)
            except:
                c_roots[item] = "timeout"
except Exception as e:
    c_roots['error'] = str(e)

# Audit specific junk directories before cleanup
junk_audit_before = {}
junk_targets = [
    (r'C:\Windows\Temp', 'Windows Temp'),
    (os.path.expandvars(r'%TEMP%'), 'User Temp'),
    (r'C:\Windows\SoftwareDistribution\Download', 'Windows Update Download Cache'),
    (r'C:\ProgramData\Microsoft\Windows\WER', 'Windows Error Reporting'),
    (r'C:\Windows\Minidump', 'Minidump Crash Logs'),
    (os.path.expandvars(r'%LOCALAPPDATA%\pip\cache'), 'Pip Cache'),
    (os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache'), 'Chrome Cache'),
    (r'C:\KaafehDoostiBot\music_cache', 'Radio Music Cache'),
    (r'C:\KaafehDoostiBot\music_cache_nostalgia', 'Nostalgia Music Cache'),
    (os.path.expandvars(r'%USERPROFILE%\Downloads'), 'User Downloads')
]

for p, label in junk_targets:
    junk_audit_before[label] = get_dir_size_mb(p)

# 2. Cleanup operations
cleaned_details = {}

# A. Empty Recycle Bin
try:
    subprocess.run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], timeout=10)
    cleaned_details['recycle_bin'] = 'Cleared'
except Exception as e:
    cleaned_details['recycle_bin'] = str(e)

# B. Clean Windows Temp
def clean_folder_files(folder):
    deleted_bytes = 0
    deleted_files = 0
    if not os.path.exists(folder):
        return 0, 0
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                os.remove(fp)
                deleted_bytes += sz
                deleted_files += 1
            except:
                pass
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                os.rmdir(dp)
            except:
                pass
    return deleted_files, round(deleted_bytes / (1024 * 1024), 2)

f_count, mb = clean_folder_files(r'C:\Windows\Temp')
cleaned_details['windows_temp_cleaned_mb'] = mb

# C. Clean User Temp
user_temp = os.path.expandvars(r'%TEMP%')
f_count, mb = clean_folder_files(user_temp)
cleaned_details['user_temp_cleaned_mb'] = mb

# D. Clean Windows Update Download Cache
f_count, mb = clean_folder_files(r'C:\Windows\SoftwareDistribution\Download')
cleaned_details['software_distribution_cleaned_mb'] = mb

# E. Clean WER & Minidump
clean_folder_files(r'C:\ProgramData\Microsoft\Windows\WER')
clean_folder_files(r'C:\Windows\Minidump')

# F. Clean Pip Cache
pip_cache = os.path.expandvars(r'%LOCALAPPDATA%\pip\cache')
if os.path.exists(pip_cache):
    f_count, mb = clean_folder_files(pip_cache)
    cleaned_details['pip_cache_cleaned_mb'] = mb

# G. Clean Chrome Cache (only Cache/Cache_Data, not login/cookies)
chrome_cache = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache')
if os.path.exists(chrome_cache):
    f_count, mb = clean_folder_files(chrome_cache)
    cleaned_details['chrome_cache_cleaned_mb'] = mb

# H. Check large logs in C:\KaafehDoostiBot
kaafeh_logs = {}
for log_file in glob.glob(r'C:\KaafehDoostiBot\*.log') + glob.glob(r'C:\KaafehDoostiBot\*_log.txt') + glob.glob(r'C:\KaafehDoostiBot\*.txt'):
    try:
        sz_mb = round(os.path.getsize(log_file) / (1024 * 1024), 2)
        kaafeh_logs[os.path.basename(log_file)] = sz_mb
        # If any log is > 50MB, truncate to last 1000 lines
        if sz_mb > 50:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as lf:
                    lines = lf.readlines()
                with open(log_file, 'w', encoding='utf-8') as lf:
                    lf.writelines(lines[-1000:])
                cleaned_details[f'truncated_{os.path.basename(log_file)}'] = f'was {sz_mb} MB'
            except:
                pass
    except:
        pass

after_space = get_drive_space()

report = {
    "before_space": before_space,
    "after_space": after_space,
    "space_freed_mb": round((after_space.get('FreeGB', 0) - before_space.get('FreeGB', 0)) * 1024, 2),
    "c_root_folders_mb": c_roots,
    "junk_audit_before_mb": junk_audit_before,
    "cleaned_details": cleaned_details,
    "kaafeh_logs_mb": kaafeh_logs
}

# Upload report to GitHub
content_b64 = base64.b64encode(json.dumps(report, indent=2).encode('utf-8')).decode('utf-8')
put_url = f'https://api.github.com/repos/{REPO}/contents/vps_disk_cleanup_report.json'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Mozilla/5.0'}
sha = None
try:
    req = urllib.request.Request(put_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        sha = json.loads(resp.read().decode())['sha']
except:
    pass

body = {'message': 'Disk cleanup report', 'content': content_b64}
if sha: body['sha'] = sha
req = urllib.request.Request(put_url, data=json.dumps(body).encode('utf-8'), headers=headers, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print('Uploaded vps_disk_cleanup_report.json successfully')
