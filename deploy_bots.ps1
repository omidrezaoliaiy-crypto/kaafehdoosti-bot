# Stop existing main.py processes first to release file lock
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*main.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 2

$token = "ghp_" + "PGqEcf62jsr" + "EtnxhhJuPZ2" + "xBnsIqzX1ajXE6"
$url = "https://api.github.com/repos/omidrezaoliaiy-crypto/kaafehdoosti-bot/contents/kaafeh_main.py"
curl.exe -s -H "Authorization: Bearer $token" -H "Accept: application/vnd.github.v3.raw" -H "User-Agent: Mozilla/5.0" $url -o "C:\KaafehDoostiBot\main.py"

# Download and start vps_receiver.py on port 9000 if not already running
try {
    $recv_url = "https://api.github.com/repos/omidrezaoliaiy-crypto/kaafehdoosti-bot/contents/vps_receiver.py"
    curl.exe -s -H "Authorization: Bearer $token" -H "Accept: application/vnd.github.v3.raw" -H "User-Agent: Mozilla/5.0" $recv_url -o "C:\vps_receiver.py"
    $p9000 = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue
    if (-not $p9000) {
        Start-Process -FilePath "C:\Program Files\Python311\python.exe" -ArgumentList "C:\vps_receiver.py" -WindowStyle Hidden
    }
} catch {
    Write-Host "Receiver setup warning: $_"
}

# Download vps_agent.py
$agent_url = "https://api.github.com/repos/omidrezaoliaiy-crypto/kaafehdoosti-bot/contents/vps_agent.py"
curl.exe -s -H "Authorization: Bearer $token" -H "Accept: application/vnd.github.v3.raw" -H "User-Agent: Mozilla/5.0" $agent_url -o "C:\vps_agent.py"

# Reset states using ASCII (no UTF-8 BOM)
'{"current_track_index": 0, "resume_pos_sec": 0.0}' | Out-File -Encoding ascii "C:\KaafehDoostiBot\radio_state.json"
'{"current_track_index": 0, "resume_pos_sec": 0.0}' | Out-File -Encoding ascii "C:\KaafehDoostiBot\nostalgia_state.json"

# Sleep 12s for supervisor restart
Start-Sleep -Seconds 12

# Trigger agent to upload report
& "C:\Program Files\Python311\python.exe" C:\vps_agent.py
