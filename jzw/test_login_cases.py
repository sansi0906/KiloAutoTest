#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""执行登录模块测试用例"""
import sys
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径到系统路径
sys.path.append('.')
from test_case_executor import TestCaseExecutor
from screenshot_manager import ScreenshotManager
from config import *

# 创建简单的TestRunner类
class SimpleRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.screenshot_dir = self.project_root / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        self.is_logged_in = False
        self.current_account = test_accounts[default_account_index]
        self.app_state = {'is_logged_in': False, 'current_page': 'unknown'}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_case_file = self.project_root / "testCase" / "app_test_cases.md"
        self.current_screenshot_dir = self.screenshot_dir / f"screenshots_{self.timestamp}"
        self.current_screenshot_dir.mkdir(exist_ok=True)

# 确保截图目录存在
screenshot_dir = r'E:\KiloAutoTest\jzw\screenshots'
os.makedirs(screenshot_dir, exist_ok=True)

# 清除App数据
print('清除App数据...')
subprocess.run('adb shell pm clear com.tjxinyu.fz', shell=True, capture_output=True)
time.sleep(2)

# 创建执行器
runner = SimpleRunner()
executor = TestCaseExecutor(runner.test_case_file, runner)

# 创建截图管理器
screenshot_manager = ScreenshotManager(runner.current_screenshot_dir)

# 执行LOG-005用例
login_cases = [c for c in executor.test_cases if c['id'] == 'LOG-005']
print(f'找到 {len(login_cases)} 个登录用例')

# 执行用例
results = []
for case in login_cases:
    print(f'\n{"="*60}')
    print(f'执行用例: {case["id"]} - {case["name"]}')
    print(f'步骤: {case["steps"]}')
    print(f'预期: {case["expected"]}')
    print(f'{"="*60}')
    
    result = executor.execute_test_case(case, screenshot_manager)
    results.append(result)
    
    # 保存截图
    if result.get('screenshot'):
        print(f'截图: {result["screenshot"]}')
    
    # 显示结果
    if result.get('status') == 'PASS':
        print(f'[OK] {case["id"]} - 通过')
    else:
        print(f'[FAIL] {case["id"]} - 失败: {result.get("message", "未知错误")}')
    
    time.sleep(3)

# 生成简单报告
print('\n' + '='*60)
print('测试结果汇总')
print('='*60)
passed = sum(1 for r in results if r.get('status') == 'PASS')
failed = len(results) - passed
for r in results:
    status = '[OK] 通过' if r.get('status') == 'PASS' else '[FAIL] 失败'
    print(f'{r.get("case_id", r.get("id", "unknown"))}: {status}')
    if r.get('message'):
        print(f'    消息: {r["message"]}')

print(f'\n总计: {len(results)} 个用例')
print(f'通过: {passed} 个')
print(f'失败: {failed} 个')
print(f'通过率: {passed/len(results)*100:.1f}%' if results else 'N/A')
