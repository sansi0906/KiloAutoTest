#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
津筑网 App 自动化测试主脚本
按用例顺序执行测试，生成测试报告和截图
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 添加项目路径到系统路径
sys.path.append(str(Path(__file__).parent))

from test_case_executor import TestCaseExecutor
from test_report_generator import TestReportGenerator
from screenshot_manager import ScreenshotManager
from config import *


class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_case_file = self.project_root / test_case_file
        self.report_dir = self.project_root / "reports"
        self.screenshot_dir = self.project_root / "screenshots"
        
        # 创建必要的目录
        self.report_dir.mkdir(exist_ok=True)
        self.screenshot_dir.mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        
        # 初始化组件
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = self.report_dir / f"test_report_{self.timestamp}.html"
        self.current_screenshot_dir = self.screenshot_dir / f"screenshots_{self.timestamp}"
        self.current_screenshot_dir.mkdir(exist_ok=True)
        
        # 登录状态管理
        self.is_logged_in = False
        self.current_account = test_accounts[default_account_index]
        
        # 初始化执行器和报告生成器
        self.executor = TestCaseExecutor(self.test_case_file, self)
        self.report_generator = TestReportGenerator(self.report_file, self.timestamp)
        self.screenshot_manager = ScreenshotManager(self.current_screenshot_dir)
        
        self.test_results = []
        
    def install_apk(self):
        """安装APK"""
        if not reinstall_apk:
            print("跳过APK安装（配置为不重新安装）")
            return True
            
        apk_full_path = self.project_root / apk_path
        
        if not apk_full_path.exists():
            print(f"警告: APK文件不存在: {apk_full_path}")
            return False
            
        print(f"开始安装APK: {apk_full_path}")
        
        try:
            # 先卸载旧版本（如果存在）
            print("  卸载旧版本...")
            cmd = f'adb uninstall {app_package}'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # 安装新APK
            print("  安装新版本...")
            cmd = f'adb install "{apk_full_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  APK安装成功")
                return True
            else:
                print(f"  APK安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  APK安装异常: {str(e)}")
            return False
    
    def login(self):
        """执行登录流程"""
        if self.is_logged_in:
            print("已登录，跳过登录步骤")
            return True
            
        print(f"执行登录流程，账号: {self.current_account['phone']}")
        
        try:
            # 启动应用
            cmd = f'adb shell am start -n {app_package}/{app_activity}'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            time.sleep(5)  # 增加等待时间
            
            # 处理隐私政策页面（等待页面加载）
            time.sleep(2)
            
            # 尝试点击同意按钮
            self._tap_coords(coordinates["privacy_agree"])
            time.sleep(3)
            
            # 检查是否进入了隐私协议详情页（如果是，需要返回）
            if self._check_privacy_detail_page():
                print("进入了隐私协议详情页，返回上一页")
                # 返回上一页
                cmd = 'adb shell input keyevent 4'  # 返回键
                subprocess.run(cmd, shell=True, capture_output=True)
                time.sleep(2)
                
                # 再次尝试点击同意按钮（可能需要稍偏上的位置）
                self._tap_coords([760, 1550])  # 稍偏上的位置
                time.sleep(3)
            
            # 输入手机号
            self._tap_coords(coordinates["phone_input"])
            time.sleep(1)
            self._input_text(self.current_account["phone"])
            time.sleep(1)
            
            # 勾选同意协议
            self._tap_coords(coordinates["agreement_checkbox"])
            time.sleep(1)
            
            # 获取验证码（这里直接使用预设验证码）
            self._tap_coords(coordinates["get_code"])
            time.sleep(3)  # 增加等待时间
            
            # 输入验证码
            self._tap_coords(coordinates["code_input"])
            time.sleep(1)
            self._input_text(self.current_account["code"])
            time.sleep(1)
            
            # 点击登录
            self._tap_coords(coordinates["login_button"])
            time.sleep(5)  # 增加等待时间
            
            # 处理授权页面（可能出现也可能不出现）
            try:
                self._tap_coords(coordinates["auth_agree"])
                time.sleep(3)
            except Exception:
                print("未检测到授权页面，继续执行")
            
            # 处理可能弹出的输入法隐私协议弹窗
            self._handle_input_method_popup()
            
            # 等待首页加载
            time.sleep(3)
            
            self.is_logged_in = True
            print("登录成功")
            return True
            
        except Exception as e:
            print(f"登录失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.is_logged_in = False
            return False
    
    def _check_privacy_detail_page(self):
        """检查是否在隐私协议详情页"""
        try:
            # 抓取当前界面文本
            cmd = 'adb shell uiautomator dump /sdcard/ui_dump.xml'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            
            cmd = 'adb pull /sdcard/ui_dump.xml /tmp/ui_dump_check.xml'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            
            import tempfile
            temp_dir = tempfile.gettempdir()
            local_path = f"{temp_dir}/ui_dump_check.xml"
            
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含隐私协议详情页特征
            if '前言' in content and '信息收集与使用' in content:
                return True
            return False
        except Exception:
            return False
    
    def _handle_input_method_popup(self):
        """处理可能弹出的输入法隐私协议弹窗"""
        # 尝试点击常见的输入法同意按钮位置（屏幕底部中间偏右）
        # 搜狗输入法等可能会弹出隐私协议
        try:
            # 尝试点击同意按钮（通常在弹窗底部）
            self._tap_coords([760, 2200])  # 常见的同意按钮位置
            time.sleep(1)
            # 可能需要再次点击（有些弹窗有多层）
            self._tap_coords([760, 2200])
            time.sleep(1)
        except Exception:
            # 如果没有弹窗，忽略错误
            pass
    
    def _tap_coords(self, coords):
        """点击坐标"""
        x, y = coords
        cmd = f'adb shell input tap {x} {y}'
        subprocess.run(cmd, shell=True, capture_output=True)
    
    def _input_text(self, text):
        """输入文本"""
        # 清除输入框
        for _ in range(20):
            subprocess.run('adb shell input keyevent KEYCODE_DEL', shell=True, capture_output=True)
        time.sleep(0.5)
        
        # 输入文本
        cmd = f'adb shell input text "{text}"'
        subprocess.run(cmd, shell=True, capture_output=True)
    
    def handle_logout(self):
        """处理退出登录后的状态"""
        self.is_logged_in = False
        print("检测到退出登录，下次用例执行前将重新登录")
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print(f"开始执行测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试报告将保存到: {self.report_file}")
        print(f"截图将保存到: {self.current_screenshot_dir}")
        print("-" * 80)
        
        # 安装APK
        if not self.install_apk():
            print("APK安装失败，尝试继续测试...")
        
        try:
            # 获取所有测试用例
            test_cases = self.executor.get_all_test_cases()
            total_cases = len(test_cases)
            
            print(f"共找到 {total_cases} 个测试用例")
            print("-" * 80)
            
            # 执行每个测试用例
            for index, test_case in enumerate(test_cases, 1):
                case_id = test_case['id']
                print(f"\n[{index}/{total_cases}] 执行测试用例: {case_id} - {test_case['name']}")
                
                # 获取当前App状态
                app_state = self.executor._get_app_state()
                
                # 检查是否需要重新登录（根据executor状态）
                if not app_state['is_logged_in']:
                    # 检查该用例是否需要登录
                    if case_id in self.executor.preconditions and 'logged_in' in self.executor.preconditions[case_id]:
                        print("  需要登录，执行登录流程...")
                        if self.login():
                            # 更新executor状态
                            self.executor._set_login_state(True)
                            self.executor._set_current_page('home')
                        else:
                            print("  登录失败，跳过此用例")
                            test_result = {
                                'id': case_id,
                                'name': test_case['name'],
                                'priority': test_case['priority'],
                                'status': 'FAIL',
                                'message': '登录失败，无法执行需要登录的用例',
                                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'duration': 0,
                                'before_screenshot': None,
                                'after_screenshot': None
                            }
                            self.test_results.append(test_result)
                            continue
                
                # 执行前截图
                before_screenshot = self.screenshot_manager.take_screenshot(f"{case_id}_before")
                
                # 执行测试用例
                result = self.executor.execute_test_case(test_case, self.screenshot_manager)
                
                # 执行后截图
                after_screenshot = self.screenshot_manager.take_screenshot(f"{case_id}_after")
                
                # 同步登录状态
                app_state = self.executor._get_app_state()
                self.is_logged_in = app_state['is_logged_in']
                
                # 记录结果
                test_result = {
                    'id': case_id,
                    'name': test_case['name'],
                    'priority': test_case['priority'],
                    'status': result['status'],
                    'message': result['message'],
                    'start_time': result['start_time'],
                    'end_time': result['end_time'],
                    'duration': result['duration'],
                    'before_screenshot': before_screenshot,
                    'after_screenshot': after_screenshot,
                    'module': test_case.get('module', '')
                }
                
                self.test_results.append(test_result)
                
                # 打印结果
                status_symbol = "✓" if result['status'] == 'PASS' else "✗"
                print(f"  状态: {status_symbol} {result['status']}")
                print(f"  耗时: {result['duration']:.2f}秒")
                if result['message']:
                    print(f"  信息: {result['message']}")
                
                # 每执行10个用例保存一次中间结果
                if index % 10 == 0:
                    self._save_intermediate_results()
            
            # 生成最终测试报告
            self._generate_final_report()
            
            # 打印测试总结
            self._print_summary()
            
        except Exception as e:
            print(f"测试执行过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    def _save_intermediate_results(self):
        """保存中间测试结果"""
        self.report_generator.generate_report(self.test_results, is_intermediate=True)
        print(f"  中间结果已保存")
    
    def _generate_final_report(self):
        """生成最终测试报告"""
        self.report_generator.generate_report(self.test_results, is_intermediate=False)
        print(f"\n最终测试报告已生成: {self.report_file}")
    
    def _print_summary(self):
        """打印测试总结"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        skipped = sum(1 for r in self.test_results if r['status'] == 'SKIP')
        
        print("\n" + "=" * 80)
        print("测试执行总结")
        print("=" * 80)
        print(f"总用例数: {total}")
        print(f"通过: {passed} ({passed/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")
        print(f"跳过: {skipped} ({skipped/total*100:.1f}%)")
        print(f"通过率: {passed/total*100:.1f}%")
        print("=" * 80)
        
        # 保存文本格式的总结
        summary_file = self.report_dir / f"test_summary_{self.timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"津筑网 App 自动化测试报告\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"时间戳: {self.timestamp}\n")
            f.write(f"测试账号: {self.current_account['phone']}\n")
            f.write("=" * 80 + "\n")
            f.write(f"总用例数: {total}\n")
            f.write(f"通过: {passed} ({passed/total*100:.1f}%)\n")
            f.write(f"失败: {failed} ({failed/total*100:.1f}%)\n")
            f.write(f"跳过: {skipped} ({skipped/total*100:.1f}%)\n")
            f.write(f"通过率: {passed/total*100:.1f}%\n")
            f.write("=" * 80 + "\n\n")
            
            # 失败用例详情
            if failed > 0:
                f.write("失败用例详情:\n")
                f.write("-" * 80 + "\n")
                for result in self.test_results:
                    if result['status'] == 'FAIL':
                        f.write(f"{result['id']} - {result['name']}\n")
                        f.write(f"  失败原因: {result['message']}\n")
                        f.write(f"  截图: {result['after_screenshot']}\n\n")
        
        print(f"测试总结已保存到: {summary_file}")


def main():
    """主函数"""
    print("津筑网 App 自动化测试系统")
    print("=" * 80)
    
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n测试执行完成！")
        return 0
    else:
        print("\n测试执行失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())