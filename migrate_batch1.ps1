# 简单迁移脚本 - 逐个迁移
$logFile = 'E:\KiloAutoTest\migration_log.txt'

function Migrate-Directory {
    param(
        [string]$SourcePath,
        [string]$DestPath,
        [string]$Name
    )
    
    $log = "[$Name] "
    Write-Output "$log开始迁移..." | Out-File $logFile -Append -Encoding UTF8
    
    # 检查源目录
    if (-not (Test-Path $SourcePath)) {
        Write-Output "$log源目录不存在，跳过" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
    
    # 检查是否已是符号链接
    $item = Get-Item $SourcePath -ErrorAction SilentlyContinue
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Write-Output "$log已是符号链接，跳过" | Out-File $logFile -Append -Encoding UTF8
        return $true
    }
    
    # 检查D盘是否已有数据
    if (-not (Test-Path $DestPath)) {
        Write-Output "$log步骤1: 复制数据到D盘..." | Out-File $logFile -Append -Encoding UTF8
        robocopy $SourcePath $DestPath /E /COPYALL /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
        if ($LASTEXITCODE -gt 7) {
            Write-Output "$log复制失败 (exit code: $LASTEXITCODE)" | Out-File $logFile -Append -Encoding UTF8
            return $false
        }
        Write-Output "$log数据复制完成" | Out-File $logFile -Append -Encoding UTF8
    }
    
    # 重命名源目录为备份
    $backupPath = $SourcePath + '.bak'
    Write-Output "$log步骤2: 重命名源目录..." | Out-File $logFile -Append -Encoding UTF8
    try {
        Move-Item -Path $SourcePath -Destination $backupPath -Force -ErrorAction Stop
    } catch {
        Write-Output "$log重命名失败: $_" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
    Start-Sleep -Seconds 1
    
    # 创建符号链接
    Write-Output "$log步骤3: 创建符号链接..." | Out-File $logFile -Append -Encoding UTF8
    $result = cmd.exe /c "mklink /J `"$SourcePath`" `"$DestPath`"" 2>&1
    Write-Output "$log链接结果: $result" | Out-File $logFile -Append -Encoding UTF8
    
    # 验证
    if (Test-Path $SourcePath) {
        $chk = Get-Item $SourcePath
        if ($chk.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Write-Output "$log✅ 迁移成功！" | Out-File $logFile -Append -Encoding UTF8
            # 删除备份
            Remove-Item -Path $backupPath -Recurse -Force -ErrorAction SilentlyContinue
            return $true
        }
    }
    
    # 失败恢复
    Write-Output "$log❌ 迁移失败，恢复..." | Out-File $logFile -Append -Encoding UTF8
    Move-Item -Path $backupPath -Destination $SourcePath -Force -ErrorAction SilentlyContinue
    return $false
}

"=== 开始迁移Local应用数据 ===" | Out-File $logFile -Append -Encoding UTF8

# 迁移列表
$migrations = @(
    @{Source = 'C:\Users\zhczz\AppData\Local\ms-playwright'; Dest = 'D:\AppData\Local\ms-playwright'; Name = 'ms-playwright'},
    @{Source = 'C:\Users\zhczz\AppData\Local\flutter_webview_windows'; Dest = 'D:\AppData\Local\flutter_webview_windows'; Name = 'flutter_webview'},
    @{Source = 'C:\Users\zhczz\AppData\Local\Google'; Dest = 'D:\AppData\Local\Google'; Name = 'Google'}
)

foreach ($m in $migrations) {
    Migrate-Directory -SourcePath $m.Source -DestPath $m.Dest -Name $m.Name
}

"=== 第一批迁移完成 ===" | Out-File $logFile -Append -Encoding UTF8
