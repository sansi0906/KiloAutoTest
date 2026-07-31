# C Drive to D Drive Migration Script
# Run with: powershell -ExecutionPolicy Bypass -File E:\KiloAutoTest\run_migration.ps1
# Close ALL apps before running this script!

$ErrorActionPreference = 'Continue'
$logFile = "$env:USERPROFILE\Desktop\migration_log.txt"
"Migration Start: $(Get-Date)" | Out-File $logFile -Encoding UTF8

function Copy-Data {
    param([string]$Source, [string]$Target, [string]$Label)
    
    Write-Host "`n[$Label] Copying data..." -ForegroundColor Cyan
    Write-Host "  From: $Source"
    Write-Host "  To: $Target"
    
    if (-not (Test-Path $Source)) {
        Write-Host "  SKIP: Source not found" -ForegroundColor Yellow
        return $false
    }
    
    $size = [math]::Round((Get-ChildItem $Source -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
    Write-Host "  Source size: $size MB"
    
    if (Test-Path $Target) {
        $existingSize = [math]::Round((Get-ChildItem $Target -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
        Write-Host "  Target exists: $existingSize MB"
        if ($existingSize -ge $size * 0.9) {
            Write-Host "  OK: Already copied, skipping" -ForegroundColor Green
            return $true
        }
        Write-Host "  Removing old data and recopying..."
        Remove-Item -Path $Target -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    try {
        Copy-Item -Path $Source -Destination $Target -Recurse -Force -ErrorAction Stop
        $newSize = [math]::Round((Get-ChildItem $Target -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
        Write-Host "  OK: Copy done $newSize MB" -ForegroundColor Green
        "[$Label] Copy OK ($newSize MB)" | Out-File $logFile -Append -Encoding UTF8
        return $true
    } catch {
        Write-Host "  FAIL: Copy failed - $_" -ForegroundColor Red
        "[$Label] Copy failed: $_" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
}

function Create-Junction {
    param([string]$Source, [string]$Target, [string]$Label)
    
    Write-Host "`n[$Label] Creating junction..." -ForegroundColor Cyan
    
    if (-not (Test-Path $Source)) {
        Write-Host "  SKIP: Source not found" -ForegroundColor Yellow
        return $false
    }
    
    $item = Get-Item $Source -ErrorAction SilentlyContinue
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Write-Host "  SKIP: Already a junction" -ForegroundColor Yellow
        return $true
    }
    
    if (-not (Test-Path $Target)) {
        Write-Host "  SKIP: Target not found on D:" -ForegroundColor Yellow
        return $false
    }
    
    $backup = $Source + '.bak'
    Write-Host "  Step 1: Rename source to backup..."
    try {
        $parent = Split-Path $Source -Parent
        $leaf = Split-Path $Source -Leaf
        Rename-Item -Path $Source -NewName ($leaf + '.bak') -Force -ErrorAction Stop
        Start-Sleep -Seconds 1
    } catch {
        Write-Host "  FAIL: Cannot rename - $_" -ForegroundColor Red
        Write-Host "  Make sure the app is closed!" -ForegroundColor Yellow
        "[$Label] Rename failed" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
    
    Write-Host "  Step 2: Create junction link..."
    try {
        New-Item -ItemType Junction -Path $Source -Target $Target -Force -ErrorAction Stop | Out-Null
        Write-Host "  OK: Junction created!" -ForegroundColor Green
        Remove-Item -Path $backup -Recurse -Force -ErrorAction SilentlyContinue
        "[$Label] Junction OK" | Out-File $logFile -Append -Encoding UTF8
        return $true
    } catch {
        Write-Host "  FAIL: $_" -ForegroundColor Red
        Write-Host "  Restoring..." -ForegroundColor Yellow
        Rename-Item -Path $backup -NewName $leaf -Force -ErrorAction SilentlyContinue
        "[$Label] Junction failed" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
}

# ============================================
# Main
# ============================================

Write-Host "`n============================================" -ForegroundColor Magenta
Write-Host "  C: to D: Data Migration Script" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "`nIMPORTANT: Close ALL apps before running!" -ForegroundColor Yellow
Write-Host "  - WPS Office"
Write-Host "  - DingTalk"
Write-Host "  - Doubao"
Write-Host "  - Chrome"
Write-Host "  - WeChat/QQ"
Write-Host "  - Trae IDE"
Write-Host "  - Any other running apps"
Write-Host "`nPress Enter to continue, or Ctrl+C to cancel..."
Read-Host

# Step 1: Copy data to D:
Write-Host "`n`n========== STEP 1: Copy Data ==========" -ForegroundColor White

$copyTasks = @(
    @{S = "$env:LOCALAPPDATA\Kingsoft"; T = "D:\AppData\Local\Kingsoft"; L = "WPS"},
    @{S = "$env:LOCALAPPDATA\DingTalk_133"; T = "D:\AppData\Local\DingTalk_133"; L = "DingTalk-Local"},
    @{S = "$env:LOCALAPPDATA\Doubao"; T = "D:\AppData\Local\Doubao"; L = "Doubao"},
    @{S = "$env:LOCALAPPDATA\ms-playwright"; T = "D:\AppData\Local\ms-playwright"; L = "Playwright"},
    @{S = "$env:LOCALAPPDATA\Google"; T = "D:\AppData\Local\Google"; L = "Chrome-Local"},
    @{S = "$env:LOCALAPPDATA\flutter_webview_windows"; T = "D:\AppData\Local\flutter_webview_windows"; L = "Flutter"},
    @{S = "$env:APPDATA\Tencent"; T = "D:\AppData\Roaming\Tencent"; L = "Tencent"},
    @{S = "$env:APPDATA\kingsoft"; T = "D:\AppData\Roaming\kingsoft"; L = "WPS-Roaming"},
    @{S = "$env:APPDATA\DingTalk"; T = "D:\AppData\Roaming\DingTalk"; L = "DingTalk-Roaming"},
    @{S = "$env:APPDATA\Trae CN"; T = "D:\AppData\Roaming\Trae CN"; L = "Trae IDE"}
)

foreach ($task in $copyTasks) {
    Copy-Data -Source $task.S -Target $task.T -Label $task.L
}

# Step 2: Create junctions
Write-Host "`n`n========== STEP 2: Create Junctions ==========" -ForegroundColor White
Write-Host "If any app is still running, close it and re-run this script" -ForegroundColor Yellow

$linkTasks = @(
    @{S = "$env:LOCALAPPDATA\Kingsoft"; T = "D:\AppData\Local\Kingsoft"; L = "WPS"},
    @{S = "$env:LOCALAPPDATA\DingTalk_133"; T = "D:\AppData\Local\DingTalk_133"; L = "DingTalk-Local"},
    @{S = "$env:LOCALAPPDATA\Doubao"; T = "D:\AppData\Local\Doubao"; L = "Doubao"},
    @{S = "$env:LOCALAPPDATA\ms-playwright"; T = "D:\AppData\Local\ms-playwright"; L = "Playwright"},
    @{S = "$env:LOCALAPPDATA\Google"; T = "D:\AppData\Local\Google"; L = "Chrome-Local"},
    @{S = "$env:LOCALAPPDATA\flutter_webview_windows"; T = "D:\AppData\Local\flutter_webview_windows"; L = "Flutter"},
    @{S = "$env:APPDATA\Tencent"; T = "D:\AppData\Roaming\Tencent"; L = "Tencent"},
    @{S = "$env:APPDATA\kingsoft"; T = "D:\AppData\Roaming\kingsoft"; L = "WPS-Roaming"},
    @{S = "$env:APPDATA\DingTalk"; T = "D:\AppData\Roaming\DingTalk"; L = "DingTalk-Roaming"},
    @{S = "$env:APPDATA\Trae CN"; T = "D:\AppData\Roaming\Trae CN"; L = "Trae IDE"}
)

$success = 0
$fail = 0
foreach ($task in $linkTasks) {
    $result = Create-Junction -Source $task.S -Target $task.T -Label $task.L
    if ($result) { $success++ } else { $fail++ }
}

# Done
Write-Host "`n`n============================================" -ForegroundColor Magenta
Write-Host "  Migration Complete!" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "`nJunctions: Success $success | Failed $fail"
Write-Host "`nLog file: $logFile"
Write-Host "`nFor failed items, close the app and re-run this script"

"Migration End: $(Get-Date)" | Out-File $logFile -Append -Encoding UTF8
"Success: $success | Failed: $fail" | Out-File $logFile -Append -Encoding UTF8
