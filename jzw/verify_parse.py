#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证测试用例解析"""
import sys
sys.path.append('.')
from test_case_executor import TestCaseExecutor
from test_login_cases import SimpleRunner
import subprocess

# 清除App数据
print('清除App数据...')
try:
    subprocess.run(['adb', 'shell', 'pm', 'clear', 'com.tjxinyu.fz'], check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    print(f'清除App数据失败: {e}')

runner = SimpleRunner()
executor = TestCaseExecutor(runner.test_case_file, runner)

# 查找LOG-001
login_cases = [c for c in executor.test_cases if c['id'] == 'LOG-001']
if login_cases:
    case = login_cases[0]
    print(f'LOG-001前置条件: {case.get("precondition", "无")}')
    print(f'LOG-001名称: {case.get("name", "无")}')
    print(f'LOG-001步骤: {case.get("steps", "无")}')
else:
    print('未找到LOG-001用例')