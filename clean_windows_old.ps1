# Windows.old 清理脚本
# 需要管理员权限运行

Write-Host "正在清理 Windows.old..." -ForegroundColor Cyan

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "错误: 需要管理员权限！" -ForegroundColor Red
    Write-Host "请右键脚本 -> 以管理员身份运行"
    Read-Host "按Enter退出"
    exit
}

$target = "C:\Windows.old"
if (-not (Test-Path $target)) {
    Write-Host "Windows.old 不存在，无需清理" -ForegroundColor Green
    Read-Host "按Enter退出"
    exit
}

# 获取所有权
Write-Host "步骤1: 获取文件所有权..."
takeown /F $target /R /D Y | Out-Null

# 授予完全权限
Write-Host "步骤2: 授予管理员完全权限..."
icacls $target /grant Administrators:F /T | Out-Null

# 删除
Write-Host "步骤3: 删除 Windows.old..."
try {
    Remove-Item -Path $target -Recurse -Force -ErrorAction Stop
    Write-Host "成功删除 Windows.old！" -ForegroundColor Green
} catch {
    Write-Host "部分文件无法删除: $_" -ForegroundColor Yellow
    Write-Host "建议重启电脑后再次运行本脚本" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "清理完成！" -ForegroundColor Cyan
Read-Host "按Enter退出"
