# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    跑测试 + 生成带时间戳的 Allure 报告 + 启动预览服务
.DESCRIPTION
    用法:
      .\run_report.ps1                                # 跑全部测试
      .\run_report.ps1 -T tests/test_login.py         # 只跑指定测试
      .\run_report.ps1 -Port 9000                     # 换端口
      .\run_report.ps1 -List                          # 只列出历史报告
#>
param(
    [string]$T = "tests/",
    [int]$Port = 8520,
    [switch]$List
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

# ── 工具函数：写无 BOM 的 UTF-8 文件 ──
function Write-Utf8NoBom($Path, $Content) {
    $enc = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

# ── 只列出历史报告 ──
if ($List) {
    Write-Host "===== 历史报告列表 =====" -ForegroundColor Yellow
    $archives = Get-ChildItem "reports/archives" -Directory -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending
    if (-not $archives) {
        Write-Host "  暂无历史报告" -ForegroundColor Gray
    } else {
        foreach ($a in $archives) {
            $n = $a.Name
            $d = "$($n.Substring(0,4))-$($n.Substring(4,2))-$($n.Substring(6,2))"
            $t = "$($n.Substring(9,2)):$($n.Substring(11,2)):$($n.Substring(13,2))"
            $info = ""
            $infoFile = Join-Path $a.FullName "run_info.txt"
            if (Test-Path $infoFile) {
                $lines = Get-Content $infoFile -Encoding utf8
                $passed = ($lines | Where-Object { $_ -match "passed=(\d+)" }) -replace ".*passed=", ""
                $failed = ($lines | Where-Object { $_ -match "failed=(\d+)" }) -replace ".*failed=", ""
                $skipped = ($lines | Where-Object { $_ -match "skipped=(\d+)" }) -replace ".*skipped=", ""
                $info = "  [P:$passed F:$failed S:$skipped]"
            }
            Write-Host "  $d $t$info  ->  reports\archives\$n" -ForegroundColor Cyan
        }
        Write-Host ""
        Write-Host "查看某次报告:" -ForegroundColor Green
        Write-Host "  python -m http.server 8520 --directory reports\archives\<时间戳>" -ForegroundColor Gray
    }
    return
}

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$tsDisplay = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$startMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

Write-Host "========================================" -ForegroundColor Yellow
Write-Host " 执行时间: $tsDisplay" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# ── 1. 备份 Allure history（用于趋势对比）──
$historyDir = "reports/allure-results/history"
$historyBackup = "reports/_history_backup"
if (Test-Path $historyDir) {
    if (Test-Path $historyBackup) { Remove-Item $historyBackup -Recurse -Force }
    Copy-Item $historyDir $historyBackup -Recurse
    Write-Host "[1/7] 备份 Allure history" -ForegroundColor Cyan
} else {
    Write-Host "[1/7] 无历史 history（首次执行）" -ForegroundColor Cyan
}

# ── 2. 运行测试 ──
Write-Host "[2/7] 运行测试: $T" -ForegroundColor Cyan
$pytestArgs = @("-m", "pytest", $T, "-v", "--tb=short",
    "--alluredir=reports/allure-results", "--clean-alluredir")
& python @pytestArgs
$testExit = $LASTEXITCODE

# 解析测试结果数量
$testSummary = "unknown"
if ($testExit -eq 0) {
    $testSummary = "all passed"
} elseif ($testExit -eq 1) {
    $testSummary = "has failures"
}

Write-Host "  测试结果: $testSummary (exit=$testExit)" -ForegroundColor Gray

# ── 3. 恢复 history ──
if (Test-Path $historyBackup) {
    New-Item -ItemType Directory -Path $historyDir -Force | Out-Null
    Copy-Item "$historyBackup/*" "$historyDir/" -Recurse -Force
    Remove-Item $historyBackup -Recurse -Force
    Write-Host "[3/7] 恢复 Allure history" -ForegroundColor Cyan
} else {
    Write-Host "[3/7] 跳过恢复 history" -ForegroundColor Cyan
}

# ── 4. 写入执行环境信息（显示在 Allure 报告中）──
# 从 .env 读取被测系统地址
$envFile = Join-Path $Root "config/.env"
$baseUrl = "unknown"
if (Test-Path $envFile) {
    $match = Get-Content $envFile -Encoding utf8 | Select-String "^BASE_URL=(.+)$"
    if ($match) { $baseUrl = $match.Matches[0].Groups[1].Value.Trim() }
}

$envContent = @"
执行时间=$tsDisplay
时间戳=$ts
被测系统=$baseUrl
浏览器=chromium
执行机=$env:COMPUTERNAME
测试结果=$testSummary
"@
Write-Utf8NoBom "reports/allure-results/environment.properties" $envContent

$executorJson = @{
    name       = "KiloAutoTest"
    type       = "local"
    buildName  = "build_$ts"
    reportName = "测试报告 $tsDisplay"
    start      = $startMs
} | ConvertTo-Json -Depth 3
Write-Utf8NoBom "reports/allure-results/executor.json" $executorJson

Write-Host "[4/7] 写入执行信息 (build=$ts)" -ForegroundColor Cyan

# ── 5. 设置 Java 环境 ──
$jdk = Get-ChildItem "C:\Program Files\Microsoft\jdk*" -Directory -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($jdk) {
    $env:JAVA_HOME = $jdk.FullName
    $env:PATH = "$($jdk.FullName)\bin;$env:PATH"
}

# ── 6. 生成带时间戳的归档报告 ──
$archiveDir = "reports/archives/$ts"
allure generate reports/allure-results -o $archiveDir --clean 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[6/7] Allure 报告生成失败" -ForegroundColor Red
    exit 1
}

# 统计测试结果数
$resultFiles = Get-ChildItem "reports/allure-results/*-result.json" -ErrorAction SilentlyContinue
$passed = ($resultFiles | Where-Object {
    (Get-Content $_.FullName -Raw) -match '"status":\s*"passed"'
}).Count
$failed = ($resultFiles | Where-Object {
    (Get-Content $_.FullName -Raw) -match '"status":\s*"failed"'
}).Count
$skipped = ($resultFiles | Where-Object {
    (Get-Content $_.FullName -Raw) -match '"status":\s*"skipped"'
}).Count
$total = $resultFiles.Count

# 在归档目录写入运行信息
$runInfo = @"
执行时间=$tsDisplay
时间戳=$ts
测试结果=$testSummary
总数=$total
passed=$passed
failed=$failed
skipped=$skipped
"@
Write-Utf8NoBom "$archiveDir/run_info.txt" $runInfo

Write-Host "[6/7] 生成归档报告: reports\archives\$ts" -ForegroundColor Cyan
Write-Host "      结果: $total total / $passed passed / $failed failed / $skipped skipped" -ForegroundColor Gray

# ── 7. 复制 history 回 allure-results（供下次执行使用）──
$newHistory = "$archiveDir/history"
if (Test-Path $newHistory) {
    if (-not (Test-Path $historyDir)) {
        New-Item -ItemType Directory -Path $historyDir -Force | Out-Null
    }
    Copy-Item "$newHistory/*" "$historyDir/" -Recurse -Force
}

# 更新 latest 指针
Write-Utf8NoBom "reports/latest.txt" $ts

# ── 历史报告列表 ──
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host " 历史报告列表（最近10次）" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
$archives = Get-ChildItem "reports/archives" -Directory -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending |
    Select-Object -First 10
foreach ($a in $archives) {
    $n = $a.Name
    $d = "$($n.Substring(0,4))-$($n.Substring(4,2))-$($n.Substring(6,2))"
    $t = "$($n.Substring(9,2)):$($n.Substring(11,2)):$($n.Substring(13,2))"
    $tag = ""
    $infoFile = Join-Path $a.FullName "run_info.txt"
    if (Test-Path $infoFile) {
        $lines = Get-Content $infoFile -Encoding utf8
        $p = ($lines | Where-Object { $_ -match "^passed=" }) -replace "passed=", ""
        $f = ($lines | Where-Object { $_ -match "^failed=" }) -replace "failed=", ""
        $s = ($lines | Where-Object { $_ -match "^skipped=" }) -replace "skipped=", ""
        $tag = "  [P:$p F:$f S:$s]"
    }
    if ($n -eq $ts) {
        Write-Host "  $d $t$tag  <- 本次" -ForegroundColor Green
    } else {
        Write-Host "  $d $t$tag" -ForegroundColor Gray
    }
}

# ── 启动服务 ──
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " 本次报告" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  执行时间: $tsDisplay" -ForegroundColor Green
Write-Host "  报告地址: http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "  归档目录: reports\archives\$ts" -ForegroundColor Green
Write-Host "  结果: $total total / $passed passed / $failed failed / $skipped skipped" -ForegroundColor Green
Write-Host "  按 Ctrl+C 退出" -ForegroundColor Green
Write-Host ""

Start-Process "http://127.0.0.1:$Port"
allure serve reports/allure-results --port $Port
