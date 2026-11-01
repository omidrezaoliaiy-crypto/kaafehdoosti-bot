[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$nvdaAppdata = "$env:APPDATA\nvda"
$addonsDir = "$nvdaAppdata\addons"
$remoteDir = "$addonsDir\remote"
New-Item -ItemType Directory -Path $remoteDir -Force | Out-Null
New-Item -ItemType Directory -Path "$nvdaAppdata\addonStore\installedAddons" -Force | Out-Null

# Download and install Remote Support 2.6.4
$addonZip = "C:\remote_2.6.4.zip"
$addonUrl = "https://github.com/NVDARemote/NVDARemote/releases/download/v2.6.4/remote-2.6.4.nvda-addon"
try {
    (New-Object Net.WebClient).DownloadFile($addonUrl, $addonZip)
    Expand-Archive -Path $addonZip -DestinationPath $remoteDir -Force
} catch {
    Write-Host "Download failed: $_"
}

# Create remote.json
$remoteJson = @'
{
  "addonId": "remote",
  "displayName": "Remote Support",
  "description": "Allows remote control of and remote access to another machine.",
  "publisher": "Tyler Spivey <tspivey@pcdesk.net>, Christopher Toth <q@q-continuum.net>",
  "addonVersionName": "2.6.4",
  "channel": "stable",
  "homepage": "https://NVDARemote.com",
  "license": "GPL v2",
  "licenseURL": "https://www.gnu.org/licenses/gpl-2.0.html",
  "sourceURL": "https://github.com/nvdaremote/nvdaremote",
  "URL": "https://github.com/NVDARemote/NVDARemote/releases/download/v2.6.4/remote-2.6.4.nvda-addon",
  "sha256": "5dec96e279b3f4b36e1f61cfd4f63230c93db3d65335833afd4aef6fcdb390be",
  "addonVersionNumber": {
    "major": 2,
    "minor": 6,
    "patch": 4
  },
  "minNVDAVersion": {
    "major": 2019,
    "minor": 3,
    "patch": 0
  },
  "lastTestedVersion": {
    "major": 2024,
    "minor": 1,
    "patch": 0
  },
  "reviewURL": "https://github.com/nvaccess/addon-datastore/discussions/2688",
  "legacy": false
}
'@
$remoteJson | Out-File -FilePath "$addonsDir\remote.json" -Encoding utf8
$remoteJson | Out-File -FilePath "$nvdaAppdata\addonStore\installedAddons\remote.json" -Encoding utf8

# Write remote.ini configured for SLAVE autoconnect
$remoteIni = @"
[connections]
	last_connected = ttdr.ir:6837, ttdr.ir
[controlserver]
	autoconnect = True
	self_hosted = False
	connection_type = 0
	host = ttdr.ir
	port = 6837
	key = !13omid81reza
[trusted_certs]
	ttdr.ir = 0f4ffc8df8d027ade74bea985c8418419ccb01b9558d2093e8fc832c17045536
[ui]
	play_sounds = True
"@
$remoteIni | Out-File -FilePath "$nvdaAppdata\remote.ini" -Encoding utf8

# Write nvda.ini with Omid's Persian speech and laptop layout settings
$nvdaIni = @"
schemaVersion = 13
[general]
	language = fa
	saveConfigurationOnExit = True
	askToExit = False
	playStartAndExitSounds = True
	loggingLevel = INFO
	showWelcomeDialogAtStartup = False
[speech]
	synth = espeak
	autoLanguageSwitching = False
	autoDialectSwitching = False
	symbolLevel = 100
	trustVoiceLanguage = True
	reportNormalizedForCharacterNavigation = True
	includeCLDR = True
	[[espeak]]
		voice = fa
		variant = max
		rate = 50
		rateBoost = True
		pitch = 40
		inflection = 75
		volume = 100
[keyboard]
	keyboardLayout = laptop
	NVDAModifierKeys = 6
	speakTypedCharacters = True
	speakTypedWords = True
[audio]
	soundVolume = 100
	audioDuckingMode = 0
"@
$nvdaIni | Out-File -FilePath "$nvdaAppdata\nvda.ini" -Encoding utf8

# Ensure Windows Audio Service is running
Start-Service -Name Audiosrv -ErrorAction SilentlyContinue

# Restart NVDA
Stop-Process -Name nvda -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

$nvdaExe = "C:\Program Files\NVDA\nvda.exe"
if (-not (Test-Path $nvdaExe)) {
    $nvdaExe = "C:\Program Files (x86)\NVDA\nvda.exe"
}

Start-Process $nvdaExe
Start-Sleep -Seconds 3

# Trigger URL handler
$urlHandler = "$remoteDir\globalPlugins\remoteClient\url_handler.exe"
if (Test-Path $urlHandler) {
    Start-Process $urlHandler -ArgumentList '"nvdaremote://ttdr.ir:6837?key=!13omid81reza&mode=slave"'
}

$proc = Get-Process nvda -ErrorAction SilentlyContinue
$status = "NVDA PID: $($proc.Id), Path: $($proc.Path), Status: SUCCESS, Time: $(Get-Date)"
$status | Out-File -FilePath "C:\nvda_status_result.txt" -Encoding utf8
