#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试验证脚本
验证测试系统各组件是否正常工作
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        return False


def check_adb_connection():
    """检查ADB连接"""
    print("\n检查ADB连接...")
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if 'device' in result.stdout:
            print("✓ ADB连接正常")
            # 获取设备信息
            devices = [line for line in result.stdout.split('\n') if 'device' in line and 'devices' not in line]
            for device in devices:
                print(f"  设备: {device.strip()}")
            return True
        else:
            print("✗ 未检测到Android设备")
            return False
    except FileNotFoundError:
        print("✗ 未找到ADB命令")
        return False


def check_app_installed():
    """检查App是否安装"""
    print("\n检查津筑网App...")
    try:
        result = subprocess.run(
            ['adb', 'shell', 'pm', 'list', 'packages'],
            capture_output=True, text=True
        )
        if 'com.tjxinyu.fz' in result.stdout:
            print("✓ 津筑网App已安装")
            return True
        else:
            print("✗ 津筑网App未安装")
            return False
    except Exception as e:
        print(f"✗ 检查App安装状态失败: {str(e)}")
        return False


def check_test_case_file():
    """检查测试用例文件"""
    print("\n检查测试用例文件...")
    test_case_file = Path(__file__).parent / "testCase" / "app_test_cases.md"
    if test_case_file.exists():
        print(f"✓ 测试用例文件存在: {test_case_file}")
        # 读取文件内容
        try:
            with open(test_case_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # 统计测试用例数量
            import re
            case_pattern = r'\|([A-Z]+-\d+[A-Za-z0-9\-]*)\|'
            cases = re.findall(case_pattern, content)
            print(f"  找到 {len(cases)} 个测试用例")
            return True
        except Exception as e:
            print(f"✗ 读取测试用例文件失败: {str(e)}")
            return False
    else:
        print(f"✗ 测试用例文件不存在: {test_case_file}")
        return False


def check_required_files():
    """检查必需的文件"""
    print("\n检查必需文件...")
    required_files = [
        "run_tests.py",
        "test_case_executor.py", 
        "test_report_generator.py",
        "screenshot_manager.py",
        "config.py"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(__file__).parent / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} 不存在")
            all_exist = False
    
    return all_exist


def check_directories():
    """检查并创建必要的目录"""
    print("\n检查目录结构...")
    directories = ["reports", "screenshots", "logs"]
    
    for dir_name in directories:
        dir_path = Path(__file__).parent / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✓ 创建目录: {dir_name}")
        else:
            print(f"✓ 目录已存在: {dir_name}")
    
    return True


def test_screenshot():
    """测试截图功能"""
    print("\n测试截图功能...")
    try:
        # 创建临时截图目录
        temp_dir = Path(__file__).parent / "screenshots" / "test"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 执行截图
        cmd = 'adb shell screencap -p /sdcard/test_screenshot.png'
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        
        # 拉取截图
        pull_cmd = f'adb pull /sdcard/test_screenshot.png "{temp_dir}/test.png"'
        subprocess.run(pull_cmd, shell=True, check=True, capture_output=True)
        
        # 清理
        cleanup_cmd = 'adb shell rm /sdcard/test_screenshot.png'
        subprocess.run(cleanup_cmd, shell=True, capture_output=True)
        
        # 检查文件
        test_file = temp_dir / "test.png"
        if test_file.exists():
            print(f"✓ 截图功能正常: {test_file}")
            # 清理测试文件
            test_file.unlink()
            return True
        else:
            print("✗ 截图文件未生成")
            return False
            
    except Exception as e:
        print(f"✗ 截图测试失败: {str(e)}")
        return False


def test_adb_commands():
    """测试常用ADB命令"""
    print("\n测试ADB命令...")
    
    test_commands = [
        ('获取设备型号', 'adb shell getprop ro.product.model'),
        ('获取Android版本', 'adb shell getprop ro.build.version.release'),
        ('获取屏幕分辨率', 'adb shell wm size'),
    ]
    
    all_success = True
    for name, cmd in test_commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"✓ {name}: {output}")
            else:
                print(f"✗ {name} 失败")
                all_success = False
        except Exception as e:
            print(f"✗ {name} 异常: {str(e)}")
            all_success = False
    
    return all_success


def main():
    """主函数"""
    print("=" * 60)
    print("津筑网 App 自动化测试系统 - 环境检查")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python_version),
        ("ADB连接", check_adb_connection),
        ("App安装", check_app_installed),
        ("测试用例文件", check_test_case_file),
        ("必需文件", check_required_files),
        ("目录结构", check_directories),
        ("截图功能", test_screenshot),
        ("ADB命令", test_adb_commands),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} 检查异常: {str(e)}")
            results.append((name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有检查通过！可以开始执行测试。")
        print("\n运行以下命令开始测试:")
        print("  python run_tests.py")
        print("  或")
        print("  start_test.bat")
        return 0
    else:
        print("\n⚠️  部分检查失败，请解决问题后重试。")
        return 1


if __name__ == "__main__":
    sys.exit(main())