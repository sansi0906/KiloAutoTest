#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
乐云泰APP测试运行脚本
"""

import os
import time
from test_case_executor import TestCaseExecutor


def run_all_tests():
    """执行所有测试用例"""
    executor = TestCaseExecutor('testCase/app_test_cases.md')
    
    # 获取所有测试用例
    test_cases = executor.get_all_test_cases()
    
    # 执行每个测试用例
    results = []
    for index, test_case in enumerate(test_cases, 1):
        print(f"\n[{index}/{len(test_cases)}] 执行测试用例: {test_case['id']} - {test_case['name']}")
        
        # 执行测试用例
        result = executor.execute_test_case(test_case)
        results.append({
            'case_id': test_case['id'],
            'case_name': test_case['name'],
            'status': result['status'],
            'message': result['message']
        })
    
    # 输出测试报告
    print("\n" + "="*80)
    print("测试报告")
    print("="*80)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    for result in results:
        status_icon = "✓" if result['status'] == 'PASS' else "✗"
        print(f"  {status_icon} {result['case_id']} - {result['case_name']}: {result['status']}")
        if result['message']:
            print(f"      {result['message']}")
    
    print("\n" + "="*80)
    print(f"总计: {len(results)} 个用例, 通过: {passed}, 失败: {failed}")
    print("="*80)


if __name__ == '__main__':
    run_all_tests()
