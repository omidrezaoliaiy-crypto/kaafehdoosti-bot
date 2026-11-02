@echo off
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = 3072; (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/extract_music_vps.py', 'C:\extract.py')"
"C:\Program Files\Python311\python.exe" -u C:\extract.py
