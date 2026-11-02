# -*- coding: utf-8 -*-
import os
import shutil
import py_compile

main_path = r"C:\KaafehDoostiBot\main.py"
bak_path = r"C:\KaafehDoostiBot\main.py.bak"

print("=== STARTING VPS PATCH ===")

if not os.path.exists(bak_path):
    shutil.copyfile(main_path, bak_path)
    print("BACKUP: Created main.py.bak")
else:
    print("BACKUP: main.py.bak exists")

with open(main_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# 1. Fix Cache Directories
orig1 = "RADIO_CACHE_DIR = os.path.join(os.getcwd(), 'music_cache')"
rep1 = 'RADIO_CACHE_DIR = os.path.join(r"C:\\KaafehDoostiBot", "music_cache")'
if orig1 in content:
    content = content.replace(orig1, rep1)
    print("CACHE_RADIO: Path fixed to C:\\KaafehDoostiBot\\music_cache")
else:
    print("CACHE_RADIO: Already updated")

orig2 = "NOSTALGIA_CACHE_DIR = os.path.join(os.getcwd(), 'music_cache_nostalgia')"
rep2 = 'NOSTALGIA_CACHE_DIR = os.path.join(r"C:\\KaafehDoostiBot", "music_cache_nostalgia")'
if orig2 in content:
    content = content.replace(orig2, rep2)
    print("CACHE_NOSTALGIA: Path fixed to C:\\KaafehDoostiBot\\music_cache_nostalgia")
else:
    print("CACHE_NOSTALGIA: Already updated")

# 2. Fix Voice Transmission
# Crucial bug: VoicePlayer called enableVoiceTransmission(False) before streaming audio blocks!
if "self.bot.enableVoiceTransmission(False)" in content:
    content = content.replace("self.bot.enableVoiceTransmission(False)", "self.bot.enableVoiceTransmission(True)", 1)
    print("VOICE_TX: Changed enableVoiceTransmission(False) to True in play_track_worker")
else:
    print("VOICE_TX: Already set to True")

# 3. Disable Cache Pruning
if "if len(files) > 4:" in content:
    content = content.replace("if len(files) > 4:", "if False and len(files) > 4:")
    print("PRUNING: Cache pruning disabled to protect all 56 songs")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("WRITE: Saved updated main.py")

# 4. Compile Check
try:
    py_compile.compile(main_path, doraise=True)
    print("SYNTAX: VERIFIED_SUCCESSFUL")
except Exception as e:
    print("SYNTAX_ERROR:", e)

print("=== VPS PATCH COMPLETE ===")
