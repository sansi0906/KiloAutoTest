#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
执行登录相关测试用例（LOG-001 到 LOG-005）
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径到系统路径
sys.path.append(str(Path(__file__).parent))

from run_tests import TestRunner
from config import app_package

def run_login_cases():
    """执行登录相关测试用例"""
    runner = TestRunner()
    
    # 获取所有测试用例
    test_cases = runner.executor.get_all_test_cases()
    
    # 筛选登录相关的用例
    login_case_ids = ['LOG-001', 'LOG-002', 'LOG-003', 'LOG-004-1', 'LOG-004-2', 'LOG-005']
    login_cases = [tc for tc in test_cases if tc['id'] in login_case_ids]
    
    print(f"找到 {len(login_cases)} 个登录相关测试用例")
    print("-" * 80)
    
    # 执行每个登录用例
    for index, test_case in enumerate(login_cases, 1):
        case_id = test_case['id']
        print(f"\n[{index}/{len(login_cases)}] 执行测试用例: {case_id} - {test_case['name']}")
        
        # 清除App数据，确保每个用例从干净状态开始
        print("  清除App数据...")
        os.system(f"adb shell pm clear {app_package}")
        import time
        time.sleep(1)
        
        # 执行测试用例
        result = runner.executor.execute_test_case(test_case, runner.screenshot_manager)
        
        # 打印结果
        status_symbol = "✓" if result['status'] == 'PASS' else "✗"
        print(f"  状态: {status_symbol} {result['status']}")
        print(f"  耗时: {result['duration']:.2f}秒")
        if result['message']:
            print(f"  信息: {result['message']}")

if __name__ == "__main__":
    run_login_cases()
