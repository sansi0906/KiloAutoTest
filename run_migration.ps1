# ============================================
# C盘应用数据迁移到D盘 - 完整脚本
# ============================================
# 请按以下步骤操作:
#   1. 关闭所有相关应用 (WPS, 钉钉, 豆包, Chrome, 微信, QQ, Trae IDE)
#   2. 右键本脚本 -> 使用PowerShell运行
#   3. 等待执行完成，查看日志
# ============================================

$ErrorActionPreference = 'Continue'
$logFile = "$env:USERPROFILE\Desktop\migration_log.txt"
"========== 迁移开始: $(Get-Date) ==========" | Out-File $logFile -Encoding UTF8

function Copy-Data {
    param([string]$Source, [string]$Target, [string]$Label)
    
    Write-Host "`n[$Label] 复制数据..." -ForegroundColor Cyan
    Write-Host "  从: $Source"
    Write-Host "  到: $Target"
    
    if (-not (Test-Path $Source)) {
        Write-Host "  ⚠️ 源不存在，跳过" -ForegroundColor Yellow
        return $false
    }
    
    $size = [math]::Round((Get-ChildItem $Source -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
    Write-Host "  源大小: $size MB"
    
    if (Test-Path $Target) {
        $existingSize = [math]::Round((Get-ChildItem $Target -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
        Write-Host "  目标已存在: $existingSize MB"
        if ($existingSize -ge $size * 0.9) {
            Write-Host "  ✅ 数据已基本复制完成，跳过" -ForegroundColor Green
            return $true
        }
        Write-Host "  移除旧数据重新复制..."
        Remove-Item -Path $Target -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    try {
        Copy-Item -Path $Source -Destination $Target -Recurse -Force -ErrorAction Stop
        $newSize = [math]::Round((Get-ChildItem $Target -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
        Write-Host "  ✅ 复制完成: $newSize MB" -ForegroundColor Green
        "[$Label] 复制成功 ($newSize MB)" | Out-File $logFile -Append -Encoding UTF8
        return $true
    } catch {
        Write-Host "  ❌ 复制失败: $_" -ForegroundColor Red
        "[$Label] 复制失败: $_" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
}

function Create-Junction {
    param([string]$Source, [string]$Target, [string]$Label)
    
    Write-Host "`n[$Label] 创建符号链接..." -ForegroundColor Cyan
    
    if (-not (Test-Path $Source)) {
        Write-Host "  ⚠️ 源不存在，跳过" -ForegroundColor Yellow
        return $false
    }
    
    $item = Get-Item $Source -ErrorAction SilentlyContinue
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Write-Host "  ⚠️ 已是符号链接，跳过" -ForegroundColor Yellow
        return $true
    }
    
    if (-not (Test-Path $Target)) {
        Write-Host "  ⚠️ D盘目标不存在，跳过" -ForegroundColor Yellow
        return $false
    }
    
    $backup = $Source + '.bak'
    Write-Host "  步骤1: 重命名源目录..."
    try {
        Rename-Item -Path $Source -NewName (Split-Path $Source -Leaf) + '.bak' -Force -ErrorAction Stop
        Start-Sleep -Seconds 1
    } catch {
        Write-Host "  ❌ 重命名失败！请关闭相关应用后重试" -ForegroundColor Red
        "[$Label] 重命名失败" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
    
    Write-Host "  步骤2: 创建Junction..."
    $result = cmd.exe /c 'mklink /J "' + $Source + '" "' + $Target + '"' 2>&1
    
    if (Test-Path $Source) {
        $chk = Get-Item $Source
        if ($chk.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Write-Host "  ✅ 成功！" -ForegroundColor Green
            Remove-Item -Path $backup -Recurse -Force -ErrorAction SilentlyContinue
            "[$Label] 链接成功" | Out-File $logFile -Append -Encoding UTF8
            return $true
        }
    }
    
    Write-Host "  ❌ 创建失败，恢复中..." -ForegroundColor Red
    Rename-Item -Path $backup -NewName (Split-Path $Source -Leaf) -Force -ErrorAction SilentlyContinue
    "[$Label] 链接失败" | Out-File $logFile -Append -Encoding UTF8
    return $false
}

# ============================================
# 主流程
# ============================================

Write-Host "`n============================================" -ForegroundColor Magenta
Write-Host "  C盘应用数据迁移脚本" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "`n⚠️  请确保已关闭以下应用:" -ForegroundColor Yellow
Write-Host "    - WPS Office"
Write-Host "    - 钉钉"
Write-Host "    - 豆包"
Write-Host "    - Chrome"
Write-Host "    - 微信/QQ"
Write-Host "    - Trae IDE"
Write-Host "    - 所有其他运行中的应用"
Write-Host "`n按Enter继续，或 Ctrl+C 取消..."
Read-Host

# 步骤1: 复制数据到D盘
Write-Host "`n`n========== 步骤1: 复制数据 ==========" -ForegroundColor White

$copyTasks = @(
    @{S = "$env:LOCALAPPDATA\Kingsoft"; T = "D:\AppData\Local\Kingsoft"; L = "WPS"},
    @{S = "$env:LOCALAPPDATA\DingTalk_133"; T = "D:\AppData\Local\DingTalk_133"; L = "钉钉-Local"},
    @{S = "$env:LOCALAPPDATA\Doubao"; T = "D:\AppData\Local\Doubao"; L = "豆包"},
    @{S = "$env:LOCALAPPDATA\ms-playwright"; T = "D:\AppData\Local\ms-playwright"; L = "Playwright"},
    @{S = "$env:LOCALAPPDATA\Google"; T = "D:\AppData\Local\Google"; L = "Chrome-Local"},
    @{S = "$env:LOCALAPPDATA\flutter_webview_windows"; T = "D:\AppData\Local\flutter_webview_windows"; L = "Flutter"},
    @{S = "$env:APPDATA\Tencent"; T = "D:\AppData\Roaming\Tencent"; L = "腾讯"},
    @{S = "$env:APPDATA\kingsoft"; T = "D:\AppData\Roaming\kingsoft"; L = "WPS-Roaming"},
    @{S = "$env:APPDATA\DingTalk"; T = "D:\AppData\Roaming\DingTalk"; L = "钉钉-Roaming"},
    @{S = "$env:APPDATA\Trae CN"; T = "D:\AppData\Roaming\Trae CN"; L = "Trae IDE"}
)

foreach ($task in $copyTasks) {
    Copy-Data -Source $task.S -Target $task.T -Label $task.L
}

# 步骤2: 创建符号链接
Write-Host "`n`n========== 步骤2: 创建符号链接 ==========" -ForegroundColor White
Write-Host "如果某个应用正在运行导致失败，请关闭后重新运行本脚本" -ForegroundColor Yellow

$linkTasks = @(
    @{S = "$env:LOCALAPPDATA\Kingsoft"; T = "D:\AppData\Local\Kingsoft"; L = "WPS"},
    @{S = "$env:LOCALAPPDATA\DingTalk_133"; T = "D:\AppData\Local\DingTalk_133"; L = "钉钉-Local"},
    @{S = "$env:LOCALAPPDATA\Doubao"; T = "D:\AppData\Local\Doubao"; L = "豆包"},
    @{S = "$env:LOCALAPPDATA\ms-playwright"; T = "D:\AppData\Local\ms-playwright"; L = "Playwright"},
    @{S = "$env:LOCALAPPDATA\Google"; T = "D:\AppData\Local\Google"; L = "Chrome-Local"},
    @{S = "$env:LOCALAPPDATA\flutter_webview_windows"; T = "D:\AppData\Local\flutter_webview_windows"; L = "Flutter"},
    @{S = "$env:APPDATA\Tencent"; T = "D:\AppData\Roaming\Tencent"; L = "腾讯"},
    @{S = "$env:APPDATA\kingsoft"; T = "D:\AppData\Roaming\kingsoft"; L = "WPS-Roaming"},
    @{S = "$env:APPDATA\DingTalk"; T = "D:\AppData\Roaming\DingTalk"; L = "钉钉-Roaming"},
    @{S = "$env:APPDATA\Trae CN"; T = "D:\AppData\Roaming\Trae CN"; L = "Trae IDE"}
)

$success = 0
$fail = 0
foreach ($task in $linkTasks) {
    $result = Create-Junction -Source $task.S -Target $task.T -Label $task.L
    if ($result) { $success++ } else { $fail++ }
}

# 完成
Write-Host "`n`n============================================" -ForegroundColor Magenta
Write-Host "  迁移完成!" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "`n链接创建: 成功 $success | 失败 $fail"
Write-Host "`n详细日志: $logFile"
Write-Host "`n如果有失败的项目，请关闭相关应用后重新运行本脚本"

"========== 迁移完成: $(Get-Date) ==========" | Out-File $logFile -Append -Encoding UTF8
