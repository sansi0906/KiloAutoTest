@echo off
chcp 65001 >nul
echo ========================================
echo 津筑网 App 自动化测试系统
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查ADB是否安装
adb version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到ADB，请先安装Android SDK Platform Tools
    pause
    exit /b 1
)

REM 检查设备连接
echo [检查] 正在检查设备连接...
adb devices | findstr "device" >nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到Android设备，请确保：
    echo   1. 设备已通过USB连接
    echo   2. 设备已开启USB调试
    echo   3. 已授权计算机调试
    pause
    exit /b 1
)

echo [成功] 设备连接正常
echo.

REM 检查App是否安装
echo [检查] 正在检查津筑网App...
adb shell pm list packages | findstr "com.tjxinyu.fz" >nul
if %errorlevel% neq 0 (
    echo [警告] 未检测到津筑网App，正在尝试安装...
    if exist "apk\xy50-test-2026-05-26 09_11_36.apk" (
        adb install "apk\xy50-test-2026-05-26 09_11_36.apk"
        if %errorlevel% neq 0 (
            echo [错误] App安装失败
            pause
            exit /b 1
        )
        echo [成功] App安装完成
    ) else (
        echo [错误] 未找到APK文件: apk\xy50-test-2026-05-26 09_11_36.apk
        pause
        exit /b 1
    )
) else (
    echo [成功] 津筑网App已安装
)

echo.
echo ========================================
echo 开始执行测试...
echo ========================================
echo.

REM 运行测试
python run_tests.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 测试执行完成！
    echo ========================================
    echo.
    echo 测试报告和截图已保存到以下目录：
    echo - 报告: reports\
    echo - 截图: screenshots\
    echo.
) else (
    echo.
    echo ========================================
    echo 测试执行失败！
    echo ========================================
    echo.
    echo 请检查错误信息并重试
    echo.
)

pause