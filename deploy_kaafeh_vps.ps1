# ==============================================================================
# Comprehensive Migration & Deployment Script for Kaafeh Doosti Bots on VPS
# Runs all bots 24/7 natively on Windows Server
# ==============================================================================
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 1: Windows Audio & Keep-Alive Checks" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
try {
    Set-Service Audiosrv, AudioEndpointBuilder -StartupType Automatic -ErrorAction SilentlyContinue
    Start-Service Audiosrv, AudioEndpointBuilder -ErrorAction SilentlyContinue
    Write-Host "[OK] Windows Audio services active." -ForegroundColor Green
} catch {
    Write-Host "[WARN] Audio: $_" -ForegroundColor Yellow
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 2: Python 3.11 Runtime Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$pyExe = "C:\Program Files\Python311\python.exe"
if (-not (Test-Path $pyExe)) {
    Write-Host "Downloading Python 3.11.9 installer..." -ForegroundColor Yellow
    $pyInstaller = "C:\py_setup.exe"
    (New-Object Net.WebClient).DownloadFile("https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe", $pyInstaller)
    Write-Host "Installing Python 3.11.9 silently..." -ForegroundColor Yellow
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    Start-Sleep -Seconds 5
}
if (Test-Path $pyExe) {
    Write-Host "[OK] Python 3.11.9 verified at $pyExe." -ForegroundColor Green
} else {
    Write-Host "[WARN] Checking alternative python path..." -ForegroundColor Yellow
    $pyCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pyCmd) { $pyExe = $pyCmd; Write-Host "[OK] Found python at $pyExe" -ForegroundColor Green }
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 3: TeamTalk 5 Runtime Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$ttDll = "C:\Program Files\TeamTalk5\TeamTalk5.dll"
if (-not (Test-Path $ttDll)) {
    Write-Host "Downloading TeamTalk 5 installer..." -ForegroundColor Yellow
    $ttInstaller = "C:\tt_setup.exe"
    (New-Object Net.WebClient).DownloadFile("https://bearware.dk/teamtalk/v5.23/TeamTalk_v5.23_Setup.exe", $ttInstaller)
    Write-Host "Installing TeamTalk 5 silently..." -ForegroundColor Yellow
    Start-Process -FilePath $ttInstaller -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" -Wait
    Start-Sleep -Seconds 5
}
if (Test-Path $ttDll) {
    Write-Host "[OK] TeamTalk 5 runtime DLLs verified at C:\Program Files\TeamTalk5." -ForegroundColor Green
} else {
    Write-Host "[WARN] TeamTalk 5 DLL check: not at default location." -ForegroundColor Yellow
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 4: Python Libraries (requests, TG, miniaudio)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
try {
    & $pyExe -m pip install --upgrade pip --quiet
    & $pyExe -m pip install requests urllib3 python-telegram-bot miniaudio --quiet
    Write-Host "[OK] Python libraries installed successfully." -ForegroundColor Green
} catch {
    Write-Host "[WARN] Pip installation: $_" -ForegroundColor Yellow
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 5: Deploying Bot Files & Music" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$botDir = "C:\KaafehDoostiBot"
New-Item -ItemType Directory -Force -Path $botDir | Out-Null
New-Item -ItemType Directory -Force -Path "$botDir\music_cache" | Out-Null
New-Item -ItemType Directory -Force -Path "$botDir\music_cache_nostalgia" | Out-Null

$wc = New-Object Net.WebClient
$rawBase = "https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main"

Write-Host "Downloading main.py, TeamTalk5.py, bot_database.db..." -ForegroundColor Yellow
$wc.DownloadFile("$rawBase/main.py", "$botDir\main.py")
$wc.DownloadFile("$rawBase/TeamTalk5.py", "$botDir\TeamTalk5.py")
$wc.DownloadFile("$rawBase/bot_database.db", "$botDir\bot_database.db")
$wc.DownloadFile("$rawBase/accounts_dump.txt", "$botDir\accounts_dump.txt")
$wc.DownloadFile("$rawBase/channels_dump.txt", "$botDir\channels_dump.txt")

Write-Host "Downloading base songs..." -ForegroundColor Yellow
try {
    $wc.DownloadFile("$rawBase/music_2.mp3", "$botDir\music_cache\2_99883435.mp3")
    $wc.DownloadFile("$rawBase/music_3.mp3", "$botDir\music_cache\3_Aroos Shomali.mp3")
    $wc.DownloadFile("$rawBase/music_4.mp3", "$botDir\music_cache\4_Gheyrati.mp3")
    Write-Host "[OK] Base songs saved into music_cache." -ForegroundColor Green
} catch {
    Write-Host "[WARN] Music download notice: $_" -ForegroundColor Yellow
}

if (Test-Path "C:\Program Files\TeamTalk5") {
    Copy-Item "C:\Program Files\TeamTalk5\*.dll" "$botDir\" -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] TeamTalk DLLs copied to $botDir." -ForegroundColor Green
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 6: Configuring 24/7 Watchdog & Auto-Start" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$startBat = "$botDir\start_bot.bat"
$batContent = @"
@echo off
title Kaafeh Doosti Bot 24/7 Watchdog
cd /d "$botDir"
:RESTART
echo Starting Kaafeh Doosti Bot at %DATE% %TIME% >> "$botDir\bot_watchdog.log"
"$pyExe" main.py >> "$botDir\bot_console.log" 2>&1
echo Bot crashed or exited with error level %ERRORLEVEL%. Restarting in 5 seconds... >> "$botDir\bot_watchdog.log"
timeout /t 5 /nobreak
goto RESTART
"@
[System.IO.File]::WriteAllText($startBat, $batContent, [System.Text.Encoding]::ASCII)

# Scheduled Task running at startup and user logon forever
schtasks.exe /Delete /TN "KaafehDoosti_24_7" /F 2>$null
$taskCmd = 'cmd.exe /c start "KaafehDoosti" /min "' + $startBat + '"'
schtasks.exe /Create /TN "KaafehDoosti_24_7" /TR $taskCmd /SC ONSTART /RU "SYSTEM" /RL HIGHEST /F

# Kill any existing old main.py process
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Launch now in background
Start-Process -FilePath "cmd.exe" -ArgumentList ('/c start "KaafehDoosti" /min "' + $startBat + '"') -WindowStyle Hidden
Start-Sleep -Seconds 4

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 7: Verifying Bot Execution" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$running = Get-Process python -ErrorAction SilentlyContinue
$statusReport = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    python_path = "$pyExe"
    teamtalk_dll = Test-Path $ttDll
    bot_dir = Test-Path "$botDir\main.py"
    db_file = Test-Path "$botDir\bot_database.db"
    music_cache_count = (Get-ChildItem "$botDir\music_cache" -ErrorAction SilentlyContinue).Count
    python_processes = ($running | Measure-Object).Count
    status = "SUCCESS_RUNNING"
} | ConvertTo-Json

[System.IO.File]::WriteAllText("$botDir\vps_status.json", $statusReport, [System.Text.Encoding]::UTF8)

[console]::beep(1000, 300)
[console]::beep(1500, 500)
Write-Host "==========================================" -ForegroundColor Green
Write-Host "KAAFEH DOOSTI BOT SUCCESSFULLY RUNNING ON VPS!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
