# Simple migration script
$logFile = 'E:\KiloAutoTest\migration_log.txt'

function Migrate-Dir {
    param([string]$Src, [string]$Dst, [string]$Name)
    $prefix = "[$Name]"
    Write-Output "$prefix Start" | Out-File $logFile -Append -Encoding UTF8
    
    if (-not (Test-Path $Src)) {
        Write-Output "$prefix Source not found, skip" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
    
    $item = Get-Item $Src -ErrorAction SilentlyContinue
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Write-Output "$prefix Already a link, skip" | Out-File $logFile -Append -Encoding UTF8
        return $true
    }
    
    if (-not (Test-Path $Dst)) {
        Write-Output "$prefix Step1: Copy to D:" | Out-File $logFile -Append -Encoding UTF8
        robocopy $Src $Dst /E /COPYALL /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
        $code = $LASTEXITCODE
        Write-Output "$prefix Copy exit code: $code" | Out-File $logFile -Append -Encoding UTF8
        if ($code -gt 7) {
            Write-Output "$prefix Copy failed" | Out-File $logFile -Append -Encoding UTF8
            return $false
        }
    }
    
    $bak = $Src + '.bak'
    Write-Output "$prefix Step2: Rename source" | Out-File $logFile -Append -Encoding UTF8
    try {
        Move-Item -Path $Src -Destination $bak -Force -ErrorAction Stop
    } catch {
        Write-Output "$prefix Rename failed: $_" | Out-File $logFile -Append -Encoding UTF8
        return $false
    }
    Start-Sleep -Seconds 1
    
    Write-Output "$prefix Step3: Create junction" | Out-File $logFile -Append -Encoding UTF8
    $cmdResult = cmd.exe /c 'mklink /J "' + $Src + '" "' + $Dst + '"' 2>&1
    Write-Output "$prefix Link: $cmdResult" | Out-File $logFile -Append -Encoding UTF8
    
    if (Test-Path $Src) {
        $chk = Get-Item $Src
        if ($chk.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Write-Output "$prefix SUCCESS" | Out-File $logFile -Append -Encoding UTF8
            Remove-Item -Path $bak -Recurse -Force -ErrorAction SilentlyContinue
            return $true
        }
    }
    
    Write-Output "$prefix FAILED, restoring" | Out-File $logFile -Append -Encoding UTF8
    Move-Item -Path $bak -Destination $Src -Force -ErrorAction SilentlyContinue
    return $false
}

Write-Output "=== Start Local migration batch1 ===" | Out-File $logFile -Append -Encoding UTF8

Migrate-Dir -Src 'C:\Users\zhczz\AppData\Local\ms-playwright' -Dst 'D:\AppData\Local\ms-playwright' -Name 'playwright'
Migrate-Dir -Src 'C:\Users\zhczz\AppData\Local\flutter_webview_windows' -Dst 'D:\AppData\Local\flutter_webview_windows' -Name 'flutter'

Write-Output "=== Batch1 done ===" | Out-File $logFile -Append -Encoding UTF8
