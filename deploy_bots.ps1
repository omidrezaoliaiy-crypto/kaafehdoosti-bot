# Stop existing main.py processes first to release file lock
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*main.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 2

$token = "ghp_" + "PGqEcf62jsr" + "EtnxhhJuPZ2" + "xBnsIqzX1ajXE6"
$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github.v3.raw"
    "User-Agent" = "Mozilla/5.0"
}
$url = "https://api.github.com/repos/omidrezaoliaiy-crypto/kaafehdoosti-bot/contents/kaafeh_main.py"
Invoke-RestMethod -Uri $url -Headers $headers -OutFile "C:\KaafehDoostiBot\main.py"

# Reset states
$state = '{"current_track_index": 0, "resume_pos_sec": 0.0}'
$state | Out-File -Encoding utf8 "C:\KaafehDoostiBot\radio_state.json"
$state | Out-File -Encoding utf8 "C:\KaafehDoostiBot\nostalgia_state.json"

# Sleep 12s for supervisor restart
Start-Sleep -Seconds 12

# Trigger agent to upload report
& "C:\Program Files\Python311\python.exe" C:\vps_agent.py
