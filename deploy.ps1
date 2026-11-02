# Clean atomic deploy
curl.exe -f -s https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/kaafeh_main.py -o "C:\KaafehDoostiBot\new_main.py"
curl.exe -f -s https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/vps_agent.py -o "C:\vps_agent.py"

if (Test-Path "C:\KaafehDoostiBot\new_main.py") {
    Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*main.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    Start-Sleep -Seconds 1
    Move-Item -Force "C:\KaafehDoostiBot\new_main.py" "C:\KaafehDoostiBot\main.py"
    Clear-Content "C:\KaafehDoostiBot\bot_console.log" -ErrorAction SilentlyContinue
}

'{"current_track_index": 0, "resume_pos_sec": 0.0}' | Out-File -Encoding ascii "C:\KaafehDoostiBot\radio_state.json"
'{"current_track_index": 0, "resume_pos_sec": 0.0}' | Out-File -Encoding ascii "C:\KaafehDoostiBot\nostalgia_state.json"

Start-Sleep -Seconds 12
& "C:\Program Files\Python311\python.exe" C:\vps_agent.py
