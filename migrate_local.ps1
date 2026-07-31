# 迁移Local应用数据到D盘
$logFile = 'E:\KiloAutoTest\migration_log.txt'
$baseLocal = 'C:\Users\zhczz\AppData\Local'
$destLocal = 'D:\AppData\Local'

# 要迁移的目录列表
$dirs = @(
    @{Name = 'Kingsoft'; SizeMB = 1377},
    @{Name = 'DingTalk_133'; SizeMB = 1006},
    @{Name = 'Doubao'; SizeMB = 606},
    @{Name = 'ms-playwright'; SizeMB = 329},
    @{Name = 'Google'; SizeMB = 98},
    @{Name = 'flutter_webview_windows'; SizeMB = 30}
)

"=== 开始迁移Local应用数据 ===" | Out-File $logFile -Append -Encoding UTF8
"创建目标目录: $destLocal" | Out-File $logFile -Append -Encoding UTF8
New-Item -ItemType Directory -Force -Path $destLocal | Out-Null

foreach ($dir in $dirs) {
    $sourcePath = Join-Path $baseLocal $dir.Name
    $destPath = Join-Path $destLocal $dir.Name
    
    if (Test-Path $sourcePath) {
        # 检查是否已经是符号链接
        $item = Get-Item $sourcePath -ErrorAction SilentlyContinue
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            "⚠️ $($dir.Name) 已经是符号链接，跳过" | Out-File $logFile -Append -Encoding UTF8
            continue
        }
        
        $destLinkPath = $sourcePath + ' - 目标: ' + $destPath
        
        "📦 迁移: $($dir.Name) ($($dir.SizeMB) MB)" | Out-File $logFile -Append -Encoding UTF8
        "   步骤1: 复制数据到D盘..." | Out-File $logFile -Append -Encoding UTF8
        
        # 复制数据到D盘
        if (-not (Test-Path $destPath)) {
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
        
        "   步骤2: 删除C盘原目录..." | Out-File $logFile -Append -Encoding UTF8
        
        # 重命名原目录（更安全）
        $backupPath = $sourcePath + '.backup_' + (Get-Date -Format 'yyyyMMddHHmmss')
        Rename-Item -Path $sourcePath -NewName $backupPath -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 0.5
        
        # 创建符号链接
        "   步骤3: 创建符号链接..." | Out-File $logFile -Append -Encoding UTF8
        cmd /c "mklink /D `"$sourcePath`" `"$destPath`"" 2>&1 | Out-File $logFile -Append -Encoding UTF8
        
        # 验证
        if (Test-Path $sourcePath) {
            $item = Get-Item $sourcePath -ErrorAction SilentlyContinue
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                "   ✅ $($dir.Name) 迁移成功！" | Out-File $logFile -Append -Encoding UTF8
                # 成功后删除备份
                Remove-Item -Path $backupPath -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                "   ❌ $($dir.Name) 迁移失败，恢复原目录" | Out-File $logFile -Append -Encoding UTF8
                Rename-Item -Path $backupPath -NewName $dir.Name -ErrorAction SilentlyContinue
            }
        } else {
            "   ❌ $($dir.Name) 符号链接创建失败，恢复原目录" | Out-File $logFile -Append -Encoding UTF8
            Rename-Item -Path $backupPath -NewName $dir.Name -ErrorAction SilentlyContinue
        }
    } else {
        "⚠️ $($dir.Name) 不存在，跳过" | Out-File $logFile -Append -Encoding UTF8
    }
}

"=== Local应用数据迁移完成 ===" | Out-File $logFile -Append -Encoding UTF8
