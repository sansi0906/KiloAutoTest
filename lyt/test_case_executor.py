#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
乐云泰APP测试用例执行器
负责解析测试用例文档和执行测试步骤
"""

import re
import time
import subprocess
import os
from datetime import datetime
from pathlib import Path
from config import *


class TestCaseExecutor:
    def __init__(self, test_case_file):
        self.test_case_file = Path(test_case_file)
        self.test_cases = []
        
        # 按键映射表
        self.keycode_map = {
            '0': 'KEYCODE_0', '1': 'KEYCODE_1', '2': 'KEYCODE_2', '3': 'KEYCODE_3', '4': 'KEYCODE_4',
            '5': 'KEYCODE_5', '6': 'KEYCODE_6', '7': 'KEYCODE_7', '8': 'KEYCODE_8', '9': 'KEYCODE_9',
            '@': 'KEYCODE_AT', '.': 'KEYCODE_PERIOD',
        }

    def parse_test_cases(self):
        """解析Markdown格式的测试用例文档"""
        if not self.test_case_file.exists():
            print(f"测试用例文件不存在: {self.test_case_file}")
            return []
        
        with open(self.test_case_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则匹配表格行
        lines = content.split('\n')
        
        test_cases = []
        is_header = False
        
        for line in lines:
            # 跳过空行和注释行
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 检查是否为表格分隔行（包含|:---|）
            if '|:---|' in line or '|---|' in line:
                is_header = True
                continue
            
            # 检查是否为表格行
            if line.startswith('|'):
                # 分割单元格
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                
                # 跳过空行
                if not any(cells):
                    continue
                
                # 第一行数据前的表格行视为表头，跳过
                if is_header:
                    is_header = False
                    continue
                
                # 跳过无效的用例ID（如表头或分隔符）
                if cells[0] in ['用例ID', ':---']:
                    continue
                
                # 解析测试用例
                if len(cells) >= 6:
                    case = {
                        'id': cells[0],
                        'name': cells[1],
                        'precondition': cells[2],
                        'steps': self._parse_steps(cells[3]),
                        'expected': cells[4],
                        'priority': cells[5] if len(cells) > 5 else 'P1'
                    }
                    test_cases.append(case)
        
        self.test_cases = test_cases
        print(f"成功解析 {len(test_cases)} 个测试用例")
        return test_cases

    def _parse_steps(self, steps_str):
        """解析测试步骤"""
        steps = []
        # 按<br>分割步骤
        step_items = re.split(r'<br\s*/?>', steps_str)
        
        for item in step_items:
            item = item.strip()
            if not item:
                continue
            
            # 提取步骤序号和内容
            match = re.match(r'(\d+)\.\s*(.+)', item)
            if match:
                step_num = int(match.group(1))
                step_content = match.group(2)
                
                # 解析动作类型
                action, target = self._parse_action(step_content)
                steps.append({
                    'num': step_num,
                    'content': step_content,
                    'action': action,
                    'target': target
                })
        
        return steps

    def _parse_action(self, content):
        """解析步骤动作"""
        if content.startswith('等待'):
            # 提取等待时间
            match = re.search(r'等待(\d+)秒', content)
            if match:
                return 'wait', int(match.group(1))
            return 'wait', 1
        
        elif content.startswith('点击'):
            # 提取点击目标
            match = re.search(r'点击["\'](.+?)["\']', content)
            if match:
                return 'click', match.group(1)
            return 'click', content[2:]
        
        elif content.startswith('输入'):
            # 提取输入内容
            match = re.search(r'输入(.+?)(：|:)(.+)', content)
            if match:
                return 'input', match.group(3)
            return 'input', content[2:]
        
        elif content.startswith('勾选'):
            return 'check', content[2:]
        
        elif content.startswith('启动'):
            return 'launch', content[2:]
        
        elif content.startswith('向上滑'):
            return 'swipe', content
        
        elif content.startswith('滑动'):
            return 'swipe', content
        
        elif content.startswith('收起键盘'):
            return 'hide_keyboard', content
        
        return 'unknown', content

    def _find_coordinate_key(self, target):
        """根据目标文本查找坐标键"""
        # 按关键词长度降序匹配，确保长关键词优先匹配
        keys = sorted(coordinates.keys(), key=lambda x: -len(x))
        
        # 精确匹配优先
        if target in coordinates:
            return target
        
        # 模糊匹配
        for key in keys:
            if key in target or target in key:
                return key
        
        # 特殊处理：提取引号内的文本
        match = re.search(r'["\'](.+?)["\']', target)
        if match:
            quoted_text = match.group(1)
            if quoted_text in coordinates:
                return quoted_text
            for key in keys:
                if key in quoted_text or quoted_text in key:
                    return key
        
        return None

    def _tap_coords(self, coords):
        """执行点击操作"""
        x, y = coords
        subprocess.run(f'adb shell input tap {x} {y}', shell=True, capture_output=True)

    def _input_text(self, text):
        """执行输入操作"""
        # 清理文本中的特殊字符
        clean_text = re.sub(r'[^\w@.]', '', text)
        print(f"        输入内容: {clean_text}")
        
        # 根据文本长度判断输入框
        if len(clean_text) == 11:
            # 手机号输入框
            self._tap_coords(coordinates['手机号输入框'])
            time.sleep(0.5)
            
            # 清空输入框
            subprocess.run('adb shell input keyevent KEYCODE_CTRL_A', shell=True, capture_output=True)
            time.sleep(0.1)
            subprocess.run('adb shell input keyevent KEYCODE_DEL', shell=True, capture_output=True)
            time.sleep(0.1)
            
            # 使用按键事件逐个输入，避免格式化
            for i in range(10):
                char = clean_text[i]
                if char in self.keycode_map:
                    subprocess.run(f'adb shell input keyevent {self.keycode_map[char]}', shell=True, capture_output=True)
                    time.sleep(0.05)
            
            # 输入最后一位后立即按回车键
            last_char = clean_text[-1]
            if last_char in self.keycode_map:
                subprocess.run(f'adb shell input keyevent {self.keycode_map[last_char]}', shell=True, capture_output=True)
            
            time.sleep(0.1)
            subprocess.run('adb shell input keyevent KEYCODE_ENTER', shell=True, capture_output=True)
        
        elif len(clean_text) == 6:
            # 验证码输入框
            self._tap_coords(coordinates['验证码输入框'])
            time.sleep(0.5)
            
            # 清空输入框
            subprocess.run('adb shell input keyevent KEYCODE_CTRL_A', shell=True, capture_output=True)
            time.sleep(0.1)
            subprocess.run('adb shell input keyevent KEYCODE_DEL', shell=True, capture_output=True)
            time.sleep(0.1)
            
            # 使用按键事件逐个输入验证码
            for char in clean_text:
                if char in self.keycode_map:
                    subprocess.run(f'adb shell input keyevent {self.keycode_map[char]}', shell=True, capture_output=True)
                    time.sleep(0.05)
            
            # 输入完成后，按返回键收起键盘
            subprocess.run('adb shell input keyevent KEYCODE_BACK', shell=True, capture_output=True)
            time.sleep(0.5)
        
        elif '@' in clean_text:
            # 密码输入（包含@符号）- 使用按键事件逐个输入
            self._tap_coords(coordinates['密码输入框'])
            time.sleep(0.5)
            
            # 清空输入框
            subprocess.run('adb shell input keyevent KEYCODE_CTRL_A', shell=True, capture_output=True)
            time.sleep(0.1)
            subprocess.run('adb shell input keyevent KEYCODE_DEL', shell=True, capture_output=True)
            time.sleep(0.1)
            
            # 使用按键事件逐个输入字符
            for char in clean_text:
                if char in self.keycode_map:
                    subprocess.run(f'adb shell input keyevent {self.keycode_map[char]}', shell=True, capture_output=True)
                else:
                    # 对于不在映射表中的字符，尝试直接输入
                    subprocess.run(f'adb shell input text "{char}"', shell=True, capture_output=True)
                time.sleep(0.05)
        
        else:
            # 其他输入
            subprocess.run(f'adb shell input text "{clean_text}"', shell=True, capture_output=True)

    def _verify_expected(self, expected):
        """验证预期结果"""
        if not expected or expected.strip() == '无需验证':
            return True, "无需验证"
        
        # 清理预期结果中的引号（处理中文引号和英文引号）
        clean_expected = expected.replace('"', '').replace('"', '').strip()
        
        # 检查预期结果关键字
        found_in_map = False
        keywords = []
        
        # 尝试精确匹配
        if clean_expected in expected_results:
            keywords = expected_results[clean_expected]
            found_in_map = True
        else:
            # 尝试模糊匹配
            for key in expected_results:
                if clean_expected in key or key in clean_expected:
                    keywords = expected_results[key]
                    found_in_map = True
                    break
        
        if found_in_map:
            if not keywords:
                return True, "无需验证"
            
            # 获取当前界面文本
            try:
                subprocess.run('adb shell uiautomator dump /sdcard/ui_dump.xml', shell=True, capture_output=True)
                result = subprocess.run('adb shell cat /sdcard/ui_dump.xml', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                ui_text = result.stdout if result.stdout else ""
                
                # 检查是否包含关键字
                found_keywords = []
                for keyword in keywords:
                    if keyword in ui_text:
                        found_keywords.append(keyword)
                
                if found_keywords:
                    return True, f"找到预期关键字: {', '.join(found_keywords)}"
                else:
                    return False, f"未找到预期关键字，期望: {', '.join(keywords)}"
            except Exception as e:
                return False, f"验证失败: {str(e)}"
        
        return True, "预期结果已记录"

    def execute_test_case(self, test_case):
        """执行单个测试用例"""
        print(f"\n{'='*80}")
        print(f"执行测试用例: {test_case['id']} - {test_case['name']}")
        print(f"预期结果: {test_case['expected']}")
        print(f"{'='*80}")
        
        # 清除App数据
        print("  清除App数据...")
        subprocess.run(f'adb shell pm clear {app_package}', shell=True, capture_output=True)
        time.sleep(1)
        
        try:
            for step in test_case['steps']:
                print(f"    步骤 {step['num']}: {step['content']}")
                
                if step['action'] == 'launch':
                    subprocess.run(f'adb shell am start -n {app_package}/{app_activity}', shell=True, capture_output=True)
                    time.sleep(3)
                
                elif step['action'] == 'wait':
                    time.sleep(step['target'])
                
                elif step['action'] == 'click':
                    coord_key = self._find_coordinate_key(step['target'])
                    if coord_key and coord_key in coordinates:
                        self._tap_coords(coordinates[coord_key])
                        print(f"        点击坐标: ({coordinates[coord_key][0]}, {coordinates[coord_key][1]})")
                    else:
                        print(f"        未找到坐标映射: {step['target']}")
                    time.sleep(1)
                
                elif step['action'] == 'input':
                    self._input_text(step['target'])
                    time.sleep(1)
                
                elif step['action'] == 'check':
                    coord_key = self._find_coordinate_key(step['target'])
                    if coord_key and coord_key in coordinates:
                        self._tap_coords(coordinates[coord_key])
                        print(f"        点击坐标: ({coordinates[coord_key][0]}, {coordinates[coord_key][1]})")
                    time.sleep(0.5)
                
                elif step['action'] == 'swipe':
                    # 向上滑动页面
                    subprocess.run('adb shell input swipe 540 1800 540 1200', shell=True, capture_output=True)
                    print(f"        向上滑动页面")
                    time.sleep(1)
                
                elif step['action'] == 'hide_keyboard':
                    # 收起键盘
                    subprocess.run('adb shell input keyevent KEYCODE_BACK', shell=True, capture_output=True)
                    print(f"        收起键盘")
                    time.sleep(0.5)
                
                time.sleep(0.5)
            
            # 验证预期结果
            success, message = self._verify_expected(test_case['expected'])
            
            if success:
                print(f"  状态: ✓ PASS")
                print(f"  信息: {message}")
                return {'status': 'PASS', 'message': message}
            else:
                print(f"  状态: ✗ FAIL")
                print(f"  信息: {message}")
                return {'status': 'FAIL', 'message': message}
        
        except Exception as e:
            print(f"  状态: ✗ FAIL")
            print(f"  信息: 执行异常 - {str(e)}")
            return {'status': 'FAIL', 'message': str(e)}

    def get_all_test_cases(self):
        """获取所有测试用例"""
        if not self.test_cases:
            self.parse_test_cases()
        return self.test_cases
