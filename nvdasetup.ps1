Start-Transcript -Path "C:\nvdasetup_full.log" -Force -Append
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "=== 0. DISABLE UAC TO PREVENT PERMISSION BLOCKS ==="
try {
    $uacPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    Set-ItemProperty -Path $uacPath -Name "EnableLUA" -Value 0 -Force
    Set-ItemProperty -Path $uacPath -Name "ConsentPromptBehaviorAdmin" -Value 0 -Force
    Write-Host "UAC disabled."
} catch {
    Write-Host "UAC config error: $_"
}

Write-Host "=== 1. POWER & SLEEP CONFIGURATION ==="
try {
    powercfg /setactive 8c5e7fda-e83b-450f-b300-e6e3d542504c
    powercfg /change monitor-timeout-ac 0
    powercfg /change monitor-timeout-dc 0
    powercfg /change standby-timeout-ac 0
    powercfg /change standby-timeout-dc 0
    powercfg /change disk-timeout-ac 0
    powercfg /change disk-timeout-dc 0
    powercfg /change hibernate-timeout-ac 0
    powercfg /change hibernate-timeout-dc 0
    powercfg -h off
    Write-Host "Power settings set to NEVER sleep / NEVER turn off."
} catch {
    Write-Host "Powercfg error: $_"
}

Write-Host "=== 2. TERMINAL SERVICES & SESSION TIMEOUT POLICIES ==="
$tsPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"
if (-not (Test-Path $tsPath)) { New-Item -Path $tsPath -Force | Out-Null }
Set-ItemProperty -Path $tsPath -Name "MaxDisconnectionTime" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $tsPath -Name "MaxIdleTime" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $tsPath -Name "MaxConnectionTime" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $tsPath -Name "fResetBroken" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $tsPath -Name "fInheritMaxDisconnectionTime" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $tsPath -Name "fInheritMaxIdleTime" -Value 0 -Type DWord -Force

$rdpTcpPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp"
if (Test-Path $rdpTcpPath) {
    Set-ItemProperty -Path $rdpTcpPath -Name "MaxDisconnectionTime" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $rdpTcpPath -Name "MaxIdleTime" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $rdpTcpPath -Name "MaxConnectionTime" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $rdpTcpPath -Name "fResetBroken" -Value 0 -Type DWord -Force
}

Write-Host "=== 3. AUTO-LOGON (SURVIVES REBOOTS) ==="
$winlogonPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty -Path $winlogonPath -Name "AutoAdminLogon" -Value "1" -Type String -Force
Set-ItemProperty -Path $winlogonPath -Name "DefaultUserName" -Value "Administrator" -Type String -Force
Set-ItemProperty -Path $winlogonPath -Name "DefaultPassword" -Value "ZJ$YZ?nGC8Ys9dP" -Type String -Force
Set-ItemProperty -Path $winlogonPath -Name "DefaultDomainName" -Value "." -Type String -Force
Set-ItemProperty -Path $winlogonPath -Name "ForceAutoLogon" -Value "1" -Type String -Force
Set-ItemProperty -Path $winlogonPath -Name "DisableCAD" -Value 1 -Type DWord -Force

Write-Host "=== 4. DISABLE LOCK SCREEN & SCREENSAVER ==="
$deskPath = "HKCU:\Control Panel\Desktop"
Set-ItemProperty -Path $deskPath -Name "ScreenSaveActive" -Value "0" -Type String -Force
Set-ItemProperty -Path $deskPath -Name "ScreenSaverIsSecure" -Value "0" -Type String -Force
Set-ItemProperty -Path $deskPath -Name "ScreenSaveTimeOut" -Value "0" -Type String -Force

$persPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization"
if (-not (Test-Path $persPath)) { New-Item -Path $persPath -Force | Out-Null }
Set-ItemProperty -Path $persPath -Name "NoLockScreen" -Value 1 -Type DWord -Force

Write-Host "=== 5. WINDOWS AUDIO SERVICE ==="
Set-Service -Name Audiosrv -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name Audiosrv -ErrorAction SilentlyContinue
Set-Service -Name AudioEndpointBuilder -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name AudioEndpointBuilder -ErrorAction SilentlyContinue

Write-Host "=== 6. NVDA & REMOTE SUPPORT CONFIGURATION ==="
$nvdaExe = "C:\Program Files (x86)\NVDA\nvda.exe"
if (-not (Test-Path $nvdaExe)) {
    $nvdaExe = "C:\Program Files\NVDA\nvda.exe"
}

if (-not (Test-Path $nvdaExe)) {
    Write-Host "NVDA not found. Installing..."
    $installerUrl = "https://www.nvaccess.org/download/nvda/releases/2024.4/nvda_2024.4.exe"
    $installerPath = "C:\nvda_installer.exe"
    try {
        (New-Object Net.WebClient).DownloadFile($installerUrl, $installerPath)
        Start-Process -FilePath $installerPath -ArgumentList "--install-silent" -Wait
        Start-Sleep -Seconds 5
    } catch {
        Write-Host "Install error: $_"
    }
}

$nvdaExe = "C:\Program Files (x86)\NVDA\nvda.exe"
if (-not (Test-Path $nvdaExe)) {
    $nvdaExe = "C:\Program Files\NVDA\nvda.exe"
}

$nvdaAppdata = "$env:APPDATA\nvda"
$addonsDir = "$nvdaAppdata\addons"
$remoteDir = "$addonsDir\remote"
New-Item -ItemType Directory -Path $remoteDir -Force | Out-Null
New-Item -ItemType Directory -Path "$nvdaAppdata\addonStore\installedAddons" -Force | Out-Null

$addonZip = "C:\remote_2.6.4.zip"
$addonUrl = "https://github.com/NVDARemote/NVDARemote/releases/download/v2.6.4/remote-2.6.4.nvda-addon"
try {
    if (-not (Test-Path "$remoteDir\manifest.ini")) {
        (New-Object Net.WebClient).DownloadFile($addonUrl, $addonZip)
        Expand-Archive -Path $addonZip -DestinationPath $remoteDir -Force
    }
} catch {
    Write-Host "Download addon failed: $_"
}

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
  "addonVersionNumber": { "major": 2, "minor": 6, "patch": 4 },
  "minNVDAVersion": { "major": 2019, "minor": 3, "patch": 0 },
  "lastTestedVersion": { "major": 2024, "minor": 1, "patch": 0 },
  "reviewURL": "https://github.com/nvaccess/addon-datastore/discussions/2688",
  "legacy": false
}
'@
$remoteJson | Out-File -FilePath "$addonsDir\remote.json" -Encoding utf8
$remoteJson | Out-File -FilePath "$nvdaAppdata\addonStore\installedAddons\remote.json" -Encoding utf8

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

$sysAppdata = "C:\Windows\System32\config\systemprofile\AppData\Roaming\nvda"
if (Test-Path "C:\Windows\System32\config\systemprofile\AppData\Roaming") {
    New-Item -ItemType Directory -Path $sysAppdata -Force | Out-Null
    Copy-Item -Path "$nvdaAppdata\*" -Destination $sysAppdata -Recurse -Force -ErrorAction SilentlyContinue
}

$defaultAppdata = "C:\Users\Default\AppData\Roaming\nvda"
if (Test-Path "C:\Users\Default\AppData\Roaming") {
    New-Item -ItemType Directory -Path $defaultAppdata -Force | Out-Null
    Copy-Item -Path "$nvdaAppdata\*" -Destination $defaultAppdata -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "=== 7. PERSISTENT WATCHDOG SCRIPT ==="
$watchdogScript = @'
$nvdaPath = "C:\Program Files (x86)\NVDA\nvda.exe"
if (-not (Test-Path $nvdaPath)) { $nvdaPath = "C:\Program Files\NVDA\nvda.exe" }
$urlHandler = "$env:APPDATA\nvda\addons\remote\globalPlugins\remoteClient\url_handler.exe"

while ($true) {
    try {
        $svc = Get-Service Audiosrv -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -ne "Running") {
            Start-Service Audiosrv -ErrorAction SilentlyContinue
        }

        $p = Get-Process nvda -ErrorAction SilentlyContinue
        if (-not $p) {
            Start-Process -FilePath $nvdaPath
            Start-Sleep -Seconds 4
            if (Test-Path $urlHandler) {
                Start-Process -FilePath $urlHandler -ArgumentList '"nvdaremote://ttdr.ir:6837?key=!13omid81reza&mode=slave"'
            }
        }

        # Keep console attached
        $qu = query user 2>&1
        if ($qu) {
            foreach ($line in ($qu | Select-Object -Skip 1)) {
                $parts = ($line.Trim() -split '\s+')
                if ($parts -contains "Disc") {
                    foreach ($val in $parts) {
                        if ($val -match '^\d+$') {
                            tscon $val /dest:console 2>&1 | Out-Null
                            break
                        }
                    }
                }
            }
        }
    } catch {
    }
    Start-Sleep -Seconds 5
}
'@
$watchdogScript | Out-File -FilePath "C:\vps_watchdog.ps1" -Encoding utf8

# Scheduled Task running as Administrator with Highest Privileges
schtasks.exe /Delete /TN "VPS_KeepAlive_Watchdog" /F 2>&1 | Out-Null
schtasks.exe /Create /TN "VPS_KeepAlive_Watchdog" /TR "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File C:\vps_watchdog.ps1" /SC ONSTART /RU "SYSTEM" /RL HIGHEST /F
schtasks.exe /Run /TN "VPS_KeepAlive_Watchdog" 2>&1 | Out-Null

Write-Host "=== 8. RESTART NVDA NOW ==="
Stop-Process -Name nvda -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
if (Test-Path $nvdaExe) {
    Start-Process -FilePath $nvdaExe
    Start-Sleep -Seconds 3
}

$urlHandler = "$remoteDir\globalPlugins\remoteClient\url_handler.exe"
if (Test-Path $urlHandler) {
    Start-Process -FilePath $urlHandler -ArgumentList '"nvdaremote://ttdr.ir:6837?key=!13omid81reza&mode=slave"'
}

$proc = Get-Process nvda -ErrorAction SilentlyContinue
$status = "NVDA PID: $($proc.Id), Watchdog Installed, AutoLogon Set, Power Tuned, Status: SUCCESS, Time: $(Get-Date)"
$status | Out-File -FilePath "C:\nvda_status_result.txt" -Encoding utf8
Write-Host $status

Stop-Transcript
