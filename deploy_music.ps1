[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = "Continue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 1: Updating main.py with VPS fixes" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$wc = New-Object Net.WebClient
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py', 'C:\KaafehDoostiBot\main.py')
Write-Host "[OK] main.py updated." -ForegroundColor Green

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 2: Downloading complete music bundle (385 MB)..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$bundleZip = "C:\music_bundle.zip"
$wc.DownloadFile('https://github.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/releases/download/v1.0.0/music_bundle.zip', $bundleZip)
$zipSize = (Get-Item $bundleZip).Length
Write-Host "[OK] Music bundle downloaded: $zipSize bytes." -ForegroundColor Green

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 3: Extracting songs into music_cache..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Expand-Archive -Path $bundleZip -DestinationPath "C:\KaafehDoostiBot" -Force
Remove-Item $bundleZip -Force -ErrorAction SilentlyContinue

$radioCount = (Get-ChildItem 'C:\KaafehDoostiBot\music_cache' -Filter *.mp3 -ErrorAction SilentlyContinue).Count
$nostalgiaCount = (Get-ChildItem 'C:\KaafehDoostiBot\music_cache_nostalgia' -Filter *.mp3 -ErrorAction SilentlyContinue).Count
Write-Host "[OK] Extraction complete! Radio songs: $radioCount, Nostalgia songs: $nostalgiaCount." -ForegroundColor Green

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 4: Restarting Bots with new music library..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
# Kill running python bot so watchdog restarts it with full library
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" -or $_.Path -like "*Python311*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 3

# If watchdog didn't restart, start via bat
$running = Get-Process python -ErrorAction SilentlyContinue
if (-not $running) {
    Start-Process -FilePath "cmd.exe" -ArgumentList ('/c start "KaafehDoosti" /min "C:\KaafehDoostiBot\start_bot.bat"') -WindowStyle Hidden
}

Start-Sleep -Seconds 5
$runningNow = (Get-Process python -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "DEPLOY_COMPLETE: Radio=$radioCount Nostalgia=$nostalgiaCount PythonProcs=$runningNow" -ForegroundColor Green
[console]::beep(1000, 300)
[console]::beep(1500, 500)
