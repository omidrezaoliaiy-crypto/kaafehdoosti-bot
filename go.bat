@echo off
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = 3072; (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/extract_music_vps.py?t=' + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds(), 'C:\extract.py')"
"C:\Program Files\Python311\python.exe" -u C:\extract.py
