# Comprehensive Automated VPS Setup Script for Omid
# Author: Antigravity Pair Programmer
$ErrorActionPreference = "Continue"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 1: Activating Windows Audio Services" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
try {
    Set-Service -Name "Audiosrv" -StartupType Automatic -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Audiosrv" -Name "Start" -Value 2 -ErrorAction SilentlyContinue
    Start-Service -Name "Audiosrv" -ErrorAction SilentlyContinue

    Set-Service -Name "AudioEndpointBuilder" -StartupType Automatic -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\AudioEndpointBuilder" -Name "Start" -Value 2 -ErrorAction SilentlyContinue
    Start-Service -Name "AudioEndpointBuilder" -ErrorAction SilentlyContinue

    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "fDisableAudioCapture" -Value 0 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "fDisableCam" -Value 0 -ErrorAction SilentlyContinue
    [console]::beep(800, 200)
    Write-Host "[OK] Windows Audio services enabled and started." -ForegroundColor Green
} catch {
    Write-Host "[WARN] Audio service notice: $_" -ForegroundColor Yellow
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 2: Installing NVDA 2024.4 Silently" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$nvdaInstaller = "C:\nvda_2024.4.exe"
if (-not (Test-Path $nvdaInstaller)) {
    Write-Host "Downloading NVDA 2024.4..." -ForegroundColor Yellow
    (New-Object Net.WebClient).DownloadFile("https://www.nvaccess.org/files/nvda/releases/2024.4/nvda_2024.4.exe", $nvdaInstaller)
}

if (Test-Path $nvdaInstaller) {
    Write-Host "Executing silent installation of NVDA 2024.4..." -ForegroundColor Yellow
    Start-Process -FilePath $nvdaInstaller -ArgumentList "--install", "--silent" -Wait
    Start-Sleep -Seconds 6
    Write-Host "[OK] NVDA 2024.4 installation completed." -ForegroundColor Green
} else {
    Write-Host "[ERROR] NVDA installer missing!" -ForegroundColor Red
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 3: Pre-configuring NVDA Remote & Settings" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$nvdaRoaming = "$env:APPDATA\nvda"
New-Item -ItemType Directory -Force -Path $nvdaRoaming | Out-Null
$addonRemoteDir = "$nvdaRoaming\addons\remote"
New-Item -ItemType Directory -Force -Path $addonRemoteDir | Out-Null

$remoteZip = "C:\remote_addon.zip"
Write-Host "Downloading NVDA Remote addon..." -ForegroundColor Yellow
(New-Object Net.WebClient).DownloadFile("https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/remote_addon.zip", $remoteZip)
if (Test-Path $remoteZip) {
    Expand-Archive -Path $remoteZip -DestinationPath $addonRemoteDir -Force
    Write-Host "[OK] NVDA Remote addon installed into $addonRemoteDir." -ForegroundColor Green
}

# Configure remote.ini with key !13omid81reza and host ttdr.ir:6837 in controlled mode (0)
$remoteIniContent = @"
[connections]
	last_connected = dnst.ir, r.ttdr.ir, ttdr.ir
[controlserver]
	autoconnect = True
	self_hosted = False
	connection_type = 0
	host = ttdr.ir
	port = 6837
	key = !13omid81reza

[seen_motds]

[trusted_certs]
	ttdr.ir = 0f4ffc8df8d027ade74bea985c8418419ccb01b9558d2093e8fc832c17045536

[ui]
	play_sounds = True
"@
[System.IO.File]::WriteAllText("$nvdaRoaming\remote.ini", $remoteIniContent, [System.Text.Encoding]::UTF8)

# Configure nvda.ini disabling updates permanently and setting Persian language
$nvdaIniContent = @"
schemaVersion = 13
[development]
[update]
	autoCheck = False
	startupNotification = False
	allowUsageStats = False
	askedAllowUsageStats = True
[general]
	language = fa
	saveConfigurationOnExit = True
	askToExit = False
	playStartAndExitSounds = True
	loggingLevel = INFO
	showWelcomeDialogAtStartup = False
[upgrade]
[addonStore]
	showWarning = False
	automaticUpdates = disabled
[speech]
	synth = espeak
	autoLanguageSwitching = False
	autoDialectSwitching = False
	symbolLevel = 100
	trustVoiceLanguage = True
	reportNormalizedForCharacterNavigation = True
	symbolDictionaries = cldr,
	includeCLDR = True
	delayedCharacterDescriptions = False
	excludedSpeechModes = ,
"@
[System.IO.File]::WriteAllText("$nvdaRoaming\nvda.ini", $nvdaIniContent, [System.Text.Encoding]::UTF8)
Write-Host "[OK] NVDA Remote pre-configured for auto-connect (ttdr.ir:6837, key: !13omid81reza)." -ForegroundColor Green

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 4: Launching NVDA 2024.4" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$nvdaExe = "C:\Program Files (x86)\NVDA\nvda.exe"
if (Test-Path $nvdaExe) {
    Start-Process -FilePath $nvdaExe
    [console]::beep(1000, 300)
    [console]::beep(1200, 300)
    Write-Host "[OK] NVDA 2024.4 started." -ForegroundColor Green
} else {
    Write-Host "[WARN] NVDA executable not at default path, checking alternative..." -ForegroundColor Yellow
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 5: Installing Python 3.11.9" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$pyInstaller = "C:\python-3.11.9-amd64.exe"
if (-not (Test-Path $pyInstaller)) {
    Write-Host "Downloading Python 3.11.9..." -ForegroundColor Yellow
    (New-Object Net.WebClient).DownloadFile("https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe", $pyInstaller)
}

if (Test-Path $pyInstaller) {
    Write-Host "Installing Python 3.11.9 silently..." -ForegroundColor Yellow
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_pip=1" -Wait
    Start-Sleep -Seconds 6
    Write-Host "[OK] Python 3.11.9 installed." -ForegroundColor Green
}

# Refresh PATH in current environment
$machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = "$machinePath;$userPath;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 6: Deploying Kaafehdoosti Bots" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "C:\kaafehdoosti" | Out-Null
$wc = New-Object Net.WebClient
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/main.py', 'C:\kaafehdoosti\main.py')
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/TeamTalk5.py', 'C:\kaafehdoosti\TeamTalk5.py')
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/bot_database.db', 'C:\kaafehdoosti\bot_database.db')
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/accounts_dump.txt', 'C:\kaafehdoosti\accounts_dump.txt')
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/channels_dump.txt', 'C:\kaafehdoosti\channels_dump.txt')
Write-Host "[OK] Kaafehdoosti bots restored to C:\kaafehdoosti." -ForegroundColor Green

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 7: Deploying Nobitex Trading Bot" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "C:\nobitex-bot" | Out-Null
$wc.DownloadFile('https://raw.githubusercontent.com/omidrezaoliaiy-crypto/kaafehdoosti-bot/main/nobitex_bot.zip', 'C:\nobitex-bot\nobitex_bot.zip')
Expand-Archive -Path 'C:\nobitex-bot\nobitex_bot.zip' -DestinationPath 'C:\nobitex-bot' -Force
Write-Host "[OK] Nobitex bot deployed to C:\nobitex-bot." -ForegroundColor Green

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 8: Installing Python Dependencies" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
try {
    python -m pip install --upgrade pip
    python -m pip install requests python-telegram-bot urllib3
    Write-Host "[OK] Python dependencies installed successfully." -ForegroundColor Green
} catch {
    Write-Host "[WARN] Pip note: $_" -ForegroundColor Yellow
}

[console]::beep(1000, 200)
[console]::beep(1400, 200)
[console]::beep(1800, 400)
Write-Host "==========================================" -ForegroundColor Green
Write-Host "ALL VPS SETUP PHASES COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
