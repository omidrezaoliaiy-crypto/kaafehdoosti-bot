# -*- coding: utf-8 -*-
import os, subprocess, time, sys, shutil

base_dir = r"C:\KaafehDoostiBot"
main_py = os.path.join(base_dir, "main.py")
kaafeh_main_py = os.path.join(base_dir, "kaafeh_main.py")
sup_py = os.path.join(base_dir, "supervisor.py")

print("=== Deploying Full Production on VPS (TeamTalk + Telegram + Soroush) ===", flush=True)

# 1. Download latest main.py and kaafeh_main.py
subprocess.run(['curl.exe', '-s', 'https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py', '-o', main_py], check=False)
subprocess.run(['curl.exe', '-s', 'https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py', '-o', kaafeh_main_py], check=False)
subprocess.run(['curl.exe', '-s', 'https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/supervisor.py', '-o', sup_py], check=False)

# 2. Patch ENABLE_TT_BOTS = True
for p in [main_py, kaafeh_main_py]:
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace('ENABLE_TT_BOTS = os.environ.get("ENABLE_TT_BOTS", "0") == "1"', 'ENABLE_TT_BOTS = True')
        c = c.replace('ENABLE_TT_BOTS = False', 'ENABLE_TT_BOTS = True')
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Patched {p} with ENABLE_TT_BOTS = True", flush=True)

# 3. Terminate any previous python processes (except ourselves)
my_pid = os.getpid()
ps_cmd = f'Get-Process python -ErrorAction SilentlyContinue | Where-Object {{ $_.Id -ne {my_pid} }} | Stop-Process -Force'
subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
time.sleep(1)

# 4. Launch supervisor detached
py_exe = r"C:\Program Files\Python311\python.exe"
p = subprocess.Popen([py_exe, sup_py], cwd=base_dir, creationflags=0x00000008) # DETACHED_PROCESS
print(f"Supervisor successfully launched with PID {p.pid}!", flush=True)
