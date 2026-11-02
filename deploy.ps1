Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*main.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 2
curl.exe -s https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/kaafeh_main.py -o "C:\KaafehDoostiBot\main.py"
curl.exe -s https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/vps_agent.py -o "C:\vps_agent.py"
'{"current_track_index": 0, "resume_pos_sec": 0.0}' | Out-File -Encoding ascii "C:\KaafehDoostiBot\radio_state.json"
'{"current_track_index": 0, "resume_pos_sec": 0.0}' | Out-File -Encoding ascii "C:\KaafehDoostiBot\nostalgia_state.json"
Start-Sleep -Seconds 14
& "C:\Program Files\Python311\python.exe" C:\vps_agent.py
