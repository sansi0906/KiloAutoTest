#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用例执行器
负责解析测试用例文档和执行测试步骤
"""

import re
import time
import subprocess
from datetime import datetime
from pathlib import Path
from config import *


class TestCaseExecutor:
    def __init__(self, test_case_file, test_runner):
        self.test_case_file = Path(test_case_file)
        self.test_runner = test_runner
        self.test_cases = []
        self.current_module = ""
        self.log_file = None
        
        # App状态管理
        self.app_state = {
            'is_logged_in': False,
            'current_page': 'unknown',  # privacy, login, auth, home, goods, order, mine, settings
            'last_operation': None,
            'errors': []
        }
        
        # 页面状态关键字映射
        self.page_state_keywords = {
            'privacy': ['请你务必审慎阅读', '服务协议', '隐私政策', '同意', '拒绝'],
            'login': ['请输入手机号', '验证码', '登录', '获取验证码', '暂不登录'],
            'auth': ['授权', '同意授权', '取消'],
            'home': ['欢迎', '交易统计', '我的消息', '全部订单', '服务生态', '服务优势', '首页'],
            'goods': ['设备', '建材', '人才', '服务', '搜索'],
            'order': ['我的订单', '待确认', '进行中', '待评价', '已完成'],
            'mine': ['我的', '收货地址', '系统设置', '成员管理'],
            'settings': ['系统设置', '退出登录', '关于我们'],
            'logout_dialog': ['提示', '您确定要退出登录吗', '确定', '取消'],
            'privacy_detail': ['隐私协议', '前言', '信息收集与使用'],
            'tip_popup': ['温馨提示', '内部账号', '暂不登录']
        }
        
        # 用例前置条件映射
        self.preconditions = {
            # 登录相关用例不需要前置登录
            'LOG-001': [],
            'LOG-002': [],
            'LOG-003': [],
            'LOG-004-1': [],
            'LOG-004-2': [],
            'LOG-005': [],
            'LOG-006': ['login'],
            'LOG-007': ['login'],
            
            # 主界面用例需要先登录
            'HOME-001': ['home', 'logged_in'],
            'HOME-002': ['home', 'logged_in'],
            'HOME-003': ['home', 'logged_in'],
            'HOME-004': ['logged_in'],
            'HOME-005': ['logged_in'],
            'HOME-006': ['logged_in'],
            'HOME-007': ['logged_in'],
            'HOME-008': ['home', 'logged_in'],
            
            # 交易统计用例需要在首页
            'STAT-001': ['home', 'logged_in'],
            'STAT-002': ['home', 'logged_in'],
            'STAT-003': ['home', 'logged_in'],
            'STAT-004': ['home', 'logged_in'],
            'STAT-005': ['home', 'logged_in'],
            'STAT-006': ['home', 'logged_in'],
            'STAT-007': ['home', 'logged_in'],
            
            # 消息模块用例需要在首页
            'MSG-001': ['home', 'logged_in'],
            'MSG-002': ['home', 'logged_in'],
            'MSG-003': ['home', 'logged_in'],
            'MSG-004': ['home', 'logged_in'],
            'MSG-005': ['home', 'logged_in'],
            'MSG-006': ['home', 'logged_in'],
            'MSG-007': ['home', 'logged_in'],
            
            # 商品页面用例
            'GOODS-001': ['goods', 'logged_in'],
            'GOODS-002': ['goods', 'logged_in'],
            'GOODS-003': ['goods', 'logged_in'],
            'GOODS-004': ['goods', 'logged_in'],
            'GOODS-005': ['goods', 'logged_in'],
            'GOODS-006': ['goods', 'logged_in'],
            'GOODS-005-1': ['goods', 'logged_in'],
            'GOODS-005-2': ['goods', 'logged_in'],
            'GOODS-005-3': ['goods', 'logged_in'],
            'GOODS-005-4': ['goods', 'logged_in'],
            'GOODS-005-5': ['goods', 'logged_in'],
            'GOODS-005-6': ['goods', 'logged_in'],
            'GOODS-005-7': ['goods', 'logged_in'],
            'GOODS-007': ['goods', 'logged_in'],
            'GOODS-008': ['goods', 'logged_in'],
            'GOODS-007-1': ['goods', 'logged_in'],
            'GOODS-007-2': ['goods', 'logged_in'],
            'GOODS-007-3': ['goods', 'logged_in'],
            'GOODS-007-4': ['goods', 'logged_in'],
            'GOODS-007-5': ['goods', 'logged_in'],
            'GOODS-007-6': ['goods', 'logged_in'],
            'GOODS-007-7': ['goods', 'logged_in'],
            'GOODS-009': ['goods', 'logged_in'],
            'GOODS-010': ['goods', 'logged_in'],
            'GOODS-010-1': ['goods', 'logged_in'],
            'GOODS-010-2': ['goods', 'logged_in'],
            'GOODS-010-3': ['goods', 'logged_in'],
            'GOODS-010-4': ['goods', 'logged_in'],
            'GOODS-010-5': ['goods', 'logged_in'],
            'GOODS-010-6': ['goods', 'logged_in'],
            'GOODS-011': ['goods', 'logged_in'],
            'GOODS-012': ['goods', 'logged_in'],
            'GOODS-013': ['goods', 'logged_in'],
            'GOODS-014': ['goods', 'logged_in'],
            'GOODS-015': ['goods', 'logged_in'],
            'GOODS-011-1': ['goods', 'logged_in'],
            'GOODS-011-2': ['goods', 'logged_in'],
            'GOODS-011-3': ['goods', 'logged_in'],
            'GOODS-011-4': ['goods', 'logged_in'],
            'GOODS-011-5': ['goods', 'logged_in'],
            'GOODS-011-6': ['goods', 'logged_in'],
            'GOODS-011-7': ['goods', 'logged_in'],
            'GOODS-016': ['goods', 'logged_in'],
            'GOODS-017': ['goods', 'logged_in'],
            'GOODS-018': ['goods', 'logged_in'],
            'GOODS-019': ['goods', 'logged_in'],
            'GOODS-020': ['logged_in'],
            'GOODS-021': ['logged_in'],
            'GOODS-022': ['logged_in'],
            
            # 我的模块用例
            'MINE-001': ['mine', 'logged_in'],
            'MINE-002': ['mine', 'logged_in'],
            'MINE-003': ['mine', 'logged_in'],
            'MINE-004': ['mine', 'logged_in'],
            'MINE-005': ['mine', 'logged_in'],
            'MINE-006': ['mine', 'logged_in'],
            'MINE-007': ['mine', 'logged_in'],
            'MINE-008': ['mine', 'logged_in'],
            'MINE-009': ['mine', 'logged_in'],
            'MINE-010': ['mine', 'logged_in'],
            'MINE-011': ['mine', 'logged_in'],
            'MINE-012': ['mine', 'logged_in'],
            'MINE-013': ['mine', 'logged_in'],
            'MINE-014': ['mine', 'logged_in'],
            'MINE-014-1': ['settings', 'logged_in'],
            'MINE-014-2': ['settings', 'logged_in'],
            'MINE-015': ['mine', 'logged_in'],
            'MINE-016': ['mine', 'logged_in'],
            'MINE-017': ['mine', 'logged_in'],
            'MINE-018': ['mine', 'logged_in'],
            
            # 订单模块用例
            'ORDER-001': ['order', 'logged_in'],
            'ORDER-002': ['order', 'logged_in'],
            'ORDER-003': ['order', 'logged_in'],
            'ORDER-004': ['order', 'logged_in'],
            'ORDER-005': ['order', 'logged_in'],
            'ORDER-006': ['order', 'logged_in'],
            'ORDER-007': ['order', 'logged_in'],
            'ORDER-007-1': ['order', 'logged_in'],
        }
        
        # 用例后置状态映射（执行成功后应该到达的状态）
        self.post_conditions = {
            'LOG-001': {'current_page': 'login', 'is_logged_in': False},
            'LOG-002': {'current_page': 'exited'},
            'LOG-003': {'current_page': 'home', 'is_logged_in': False},
            'LOG-004-1': {'current_page': 'login', 'is_logged_in': False},
            'LOG-004-2': {'current_page': 'home', 'is_logged_in': False},
            'LOG-005': {'current_page': 'home', 'is_logged_in': True},
            'LOG-006': {'current_page': 'home', 'is_logged_in': False},
            'LOG-007': {'current_page': 'login', 'is_logged_in': False},
            
            'HOME-001': {'current_page': 'home'},
            'HOME-002': {'current_page': 'home'},
            'HOME-003': {'current_page': 'home'},
            'HOME-004': {'current_page': 'home'},
            'HOME-005': {'current_page': 'order'},
            'HOME-006': {'current_page': 'goods'},
            'HOME-007': {'current_page': 'mine'},
            'HOME-008': {'current_page': 'order'},
            
            'STAT-001': {'current_page': 'home'},
            'STAT-002': {'current_page': 'home'},
            'STAT-003': {'current_page': 'home'},
            'STAT-004': {'current_page': 'home'},
            'STAT-005': {'current_page': 'home'},
            'STAT-006': {'current_page': 'home'},
            'STAT-007': {'current_page': 'home'},
            
            'MSG-001': {'current_page': 'home'},
            'MSG-002': {'current_page': 'home'},
            'MSG-003': {'current_page': 'home'},
            'MSG-004': {'current_page': 'home'},
            'MSG-005': {'current_page': 'home'},
            'MSG-006': {'current_page': 'home'},
            'MSG-007': {'current_page': 'message'},
            
            'GOODS-001': {'current_page': 'goods'},
            'GOODS-002': {'current_page': 'goods'},
            'GOODS-003': {'current_page': 'goods'},
            'GOODS-004': {'current_page': 'goods'},
            'GOODS-005': {'current_page': 'goods'},
            'GOODS-006': {'current_page': 'goods'},
            'GOODS-005-1': {'current_page': 'goods'},
            'GOODS-005-2': {'current_page': 'goods'},
            'GOODS-005-3': {'current_page': 'goods'},
            'GOODS-005-4': {'current_page': 'goods'},
            'GOODS-005-5': {'current_page': 'goods'},
            'GOODS-005-6': {'current_page': 'goods_detail'},
            'GOODS-005-7': {'current_page': 'goods'},
            'GOODS-007': {'current_page': 'goods'},
            'GOODS-008': {'current_page': 'goods'},
            'GOODS-007-1': {'current_page': 'goods'},
            'GOODS-007-2': {'current_page': 'goods'},
            'GOODS-007-3': {'current_page': 'goods'},
            'GOODS-007-4': {'current_page': 'goods'},
            'GOODS-007-5': {'current_page': 'goods'},
            'GOODS-007-6': {'current_page': 'goods_detail'},
            'GOODS-007-7': {'current_page': 'goods'},
            'GOODS-009': {'current_page': 'goods'},
            'GOODS-010': {'current_page': 'goods'},
            'GOODS-010-1': {'current_page': 'goods'},
            'GOODS-010-2': {'current_page': 'goods'},
            'GOODS-010-3': {'current_page': 'goods'},
            'GOODS-010-4': {'current_page': 'goods'},
            'GOODS-010-5': {'current_page': 'goods'},
            'GOODS-010-6': {'current_page': 'goods_detail'},
            'GOODS-010-7': {'current_page': 'goods'},
            'GOODS-011': {'current_page': 'goods'},
            'GOODS-012': {'current_page': 'goods'},
            'GOODS-013': {'current_page': 'goods'},
            'GOODS-014': {'current_page': 'goods'},
            'GOODS-015': {'current_page': 'goods'},
            'GOODS-011-1': {'current_page': 'goods'},
            'GOODS-011-2': {'current_page': 'goods'},
            'GOODS-011-3': {'current_page': 'goods'},
            'GOODS-011-4': {'current_page': 'goods'},
            'GOODS-011-5': {'current_page': 'goods'},
            'GOODS-011-6': {'current_page': 'goods_detail'},
            'GOODS-011-7': {'current_page': 'goods'},
            'GOODS-016': {'current_page': 'goods'},
            'GOODS-017': {'current_page': 'goods'},
            'GOODS-018': {'current_page': 'goods'},
            'GOODS-019': {'current_page': 'goods'},
            'GOODS-020': {'current_page': 'home'},
            'GOODS-021': {'current_page': 'order'},
            'GOODS-022': {'current_page': 'mine'},
            
            'MINE-001': {'current_page': 'mine'},
            'MINE-002': {'current_page': 'mine'},
            'MINE-003': {'current_page': 'mine'},
            'MINE-004': {'current_page': 'mine'},
            'MINE-005': {'current_page': 'member_manage'},
            'MINE-006': {'current_page': 'mine'},
            'MINE-007': {'current_page': 'mine'},
            'MINE-008': {'current_page': 'mine'},
            'MINE-009': {'current_page': 'mine'},
            'MINE-010': {'current_page': 'mine'},
            'MINE-011': {'current_page': 'address'},
            'MINE-012': {'current_page': 'qualification'},
            'MINE-013': {'current_page': 'feedback'},
            'MINE-014': {'current_page': 'settings'},
            'MINE-014-1': {'current_page': 'login', 'is_logged_in': False},
            'MINE-014-2': {'current_page': 'settings', 'is_logged_in': True},
            'MINE-015': {'current_page': 'about'},
            'MINE-016': {'current_page': 'home'},
            'MINE-017': {'current_page': 'order'},
            'MINE-018': {'current_page': 'goods'},
            
            'ORDER-001': {'current_page': 'order'},
            'ORDER-002': {'current_page': 'order'},
            'ORDER-003': {'current_page': 'order'},
            'ORDER-004': {'current_page': 'order'},
            'ORDER-005': {'current_page': 'order'},
            'ORDER-006': {'current_page': 'order'},
            'ORDER-007': {'current_page': 'order'},
            'ORDER-007-1': {'current_page': 'order'},
        }
        
        # 初始化日志文件
        self._init_log_file()
        
        # 解析测试用例
        self._parse_test_cases()
    
    def _init_log_file(self):
        """初始化日志文件"""
        from datetime import datetime
        log_dir = self.test_case_file.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"test_execution_{timestamp}.log"
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"测试执行日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
    
    def _log_debug(self, message):
        """记录调试日志"""
        if self.log_file:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] DEBUG: {message}\n")
    
    def _log_error(self, message):
        """记录错误日志"""
        if self.log_file:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] ERROR: {message}\n")
    
    def _detect_current_page(self):
        """检测当前页面"""
        xml_content = self._dump_ui_hierarchy()
        if not xml_content:
            return 'unknown'
        
        texts = re.findall(r'text="([^"]+)"', xml_content)
        all_text = ' '.join(texts)
        
        # 根据关键字匹配页面
        for page, keywords in self.page_state_keywords.items():
            matched_count = sum(1 for kw in keywords if kw in all_text)
            if matched_count >= len(keywords) * 0.5:  # 匹配超过一半关键字
                return page
        
        return 'unknown'
    
    def _trigger_tip_popup(self):
        """触发内部账号弹窗（执行LOG-004完整流程）"""
        try:
            # 清除App数据并重启
            subprocess.run('adb shell pm clear com.tjxinyu.fz', shell=True, capture_output=True)
            time.sleep(2)
            subprocess.run('adb shell am start -n com.tjxinyu.fz/com.tarodemo.PrivacyActivity', shell=True, capture_output=True)
            time.sleep(3)

            # 点击隐私页"同意"按钮
            self._tap_coords(coordinates['privacy_agree'])
            time.sleep(2)

            # 点击"本机号码一键登录"
            self._tap_coords(coordinates['one_key_login'])
            time.sleep(3)

            # 点击弹窗"同意"按钮
            self._tap_coords(coordinates['auth_agree'])
            time.sleep(5)

            # 检查弹窗是否出现
            current_page = self._detect_current_page()
            if current_page == 'tip_popup':
                return True, "内部账号弹窗已显示"
            return False, f"弹窗未显示，当前页面: {current_page}"
        except Exception as e:
            return False, str(e)

    def _verify_preconditions(self, case_id):
        """验证前置条件"""
        if case_id not in self.preconditions:
            return True, "无前置条件"
        
        required_conditions = self.preconditions[case_id]
        missing_conditions = []
        
        # 检测当前页面
        current_page = self._detect_current_page()
        self.app_state['current_page'] = current_page

        # 检查登录状态条件
        if 'logged_in' in required_conditions and not self.app_state['is_logged_in']:
            missing_conditions.append('需要登录状态')

        # 检查页面条件
        for condition in required_conditions:
            if condition == 'logged_in':
                continue
            if condition == 'tip_popup_shown':
                # 检查内部账号弹窗是否显示
                if current_page == 'tip_popup':
                    # 弹窗已显示，直接通过
                    continue
                elif current_page == 'auth':
                    # 当前在授权弹窗（弹窗1），需要再次点击同意触发弹窗2
                    self._log_debug("当前在授权弹窗，点击同意触发内部账号弹窗")
                    self._tap_coords(coordinates['auth_agree'])
                    time.sleep(5)
                    current_page = self._detect_current_page()
                    if current_page != 'tip_popup':
                        missing_conditions.append(f"无法触发内部账号弹窗，当前页面: {current_page}")
                else:
                    # 尝试触发内部账号弹窗（执行LOG-004流程）
                    self._log_debug("内部账号弹窗未显示，尝试触发")
                    success, msg = self._trigger_tip_popup()
                    if not success:
                        missing_conditions.append(f"无法触发内部账号弹窗: {msg}")
                    else:
                        current_page = self._detect_current_page()
                        if current_page != 'tip_popup':
                            missing_conditions.append(f"触发后仍未在tip_popup页面，当前页面: {current_page}")
                continue
            if condition != current_page:
                missing_conditions.append(f"需要在{condition}页面，当前在{current_page}页面")        
        if missing_conditions:
            return False, "; ".join(missing_conditions)
        
        return True, f"前置条件满足: 当前页面={current_page}, 登录状态={self.app_state['is_logged_in']}"
    
    def _update_post_conditions(self, case_id, success):
        """更新后置状态"""
        if not success or case_id not in self.post_conditions:
            return
        
        post_state = self.post_conditions[case_id]
        
        if 'current_page' in post_state:
            self.app_state['current_page'] = post_state['current_page']
        
        if 'is_logged_in' in post_state:
            self.app_state['is_logged_in'] = post_state['is_logged_in']
        
        self._log_debug(f"更新状态: {self.app_state}")
    
    def _get_app_state(self):
        """获取当前App状态"""
        return self.app_state
    
    def _reset_app_state(self):
        """重置App状态"""
        self.app_state = {
            'is_logged_in': False,
            'current_page': 'unknown',
            'last_operation': None,
            'errors': []
        }
    
    def _set_login_state(self, is_logged_in):
        """设置登录状态"""
        self.app_state['is_logged_in'] = is_logged_in
    
    def _set_current_page(self, page):
        """设置当前页面"""
        self.app_state['current_page'] = page
    
    def _parse_test_cases(self):
        """解析测试用例文档"""
        if not self.test_case_file.exists():
            print(f"测试用例文件不存在: {self.test_case_file}")
            return
        
        with open(self.test_case_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按模块分割
        modules = re.split(r'##\s+(.*?)\s*\n', content)
        
        for i in range(1, len(modules), 2):
            module_name = modules[i].strip()
            module_content = modules[i+1]
            
            # 跳过文档信息模块（非测试用例）
            if module_name.startswith('一、文档信息') or module_name.startswith('文档信息'):
                continue
            
            # 查找模块下的表格（支持5列或6列格式）
            table_pattern_5col = r'\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|'
            table_pattern_6col = r'\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|'
            
            # 先尝试6列格式（包含前置条件）
            matches = re.findall(table_pattern_6col, module_content)
            has_precondition = True
            
            # 如果没有匹配到6列，尝试5列格式
            if not matches:
                matches = re.findall(table_pattern_5col, module_content)
                has_precondition = False
            
            for match in matches:
                case_id = match[0].strip()
                case_name = match[1].strip()
                
                if has_precondition:
                    case_precondition = match[2].strip()
                    case_steps = match[3].strip()
                    case_expected = match[4].strip()
                    case_priority = match[5].strip()
                else:
                    case_precondition = ''
                    case_steps = match[2].strip()
                    case_expected = match[3].strip()
                    case_priority = match[4].strip()
                
                # 跳过表头和分隔行
                if case_id in ['用例ID', '----', '', '项目'] or not case_id or case_id.startswith('---'):
                    continue
                
                # 跳过非测试用例行（如文档信息表格中的行）
                if case_id in ['文档版本', '创建日期', '适用版本', '测试设备']:
                    continue
                
                self.test_cases.append({
                    'id': case_id,
                    'name': case_name,
                    'precondition': case_precondition,
                    'steps': case_steps,
                    'expected': case_expected,
                    'priority': case_priority,
                    'module': module_name
                })
        
        print(f"成功解析 {len(self.test_cases)} 个测试用例")
    
    def get_all_test_cases(self):
        """获取所有测试用例"""
        return self.test_cases
    
    def execute_test_case(self, test_case, screenshot_manager):
        """执行单个测试用例"""
        start_time = datetime.now()
        case_id = test_case['id']
        
        # 记录用例开始执行
        self._log_debug(f"开始执行测试用例: {case_id} - {test_case['name']}")
        
        try:
            # ========== 前置条件验证 ==========
            self._log_debug(f"验证前置条件")
            pre_success, pre_message = self._verify_preconditions(case_id)
            
            if not pre_success:
                self._log_error(f"前置条件不满足: {pre_message}")
                screenshot_manager.take_screenshot(f"{case_id}_precondition_failed")
                return {
                    'status': 'FAIL',
                    'message': f"前置条件不满足: {pre_message}",
                    'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': (datetime.now() - start_time).total_seconds()
                }
            
            print(f"    前置条件: {pre_message}")
            self._log_debug(f"前置条件满足: {pre_message}")
            
            # ========== 解析并执行步骤 ==========
            steps = self._parse_steps(test_case['steps'])
            
            for step_index, step in enumerate(steps):
                print(f"    步骤 {step_index + 1}: {step['description']}")
                self._log_debug(f"执行步骤 {step_index + 1}: {step['description']}")
                
                # 执行步骤
                success, message = self._execute_step(step)
                
                if not success:
                    # 记录错误日志
                    self._log_error(f"步骤 {step_index + 1} 执行失败: {message}")
                    # 失败时截图
                    screenshot_manager.take_screenshot(f"{case_id}_step{step_index + 1}_failed")
                    return {
                        'status': 'FAIL',
                        'message': f"步骤 {step_index + 1} 执行失败: {message}",
                        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'duration': (datetime.now() - start_time).total_seconds()
                    }
                
                # 步骤截图
                screenshot_manager.take_screenshot(f"{case_id}_step{step_index + 1}")
                
                # 步骤执行后验证（关键步骤）
                verify_success, verify_msg = self._verify_step_result(step, step_index + 1)
                if not verify_success:
                    self._log_error(f"步骤 {step_index + 1} 验证失败: {verify_msg}")
                    screenshot_manager.take_screenshot(f"{case_id}_step{step_index + 1}_verify_failed")
                    return {
                        'status': 'FAIL',
                        'message': f"步骤 {step_index + 1} 验证失败: {verify_msg}",
                        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'duration': (datetime.now() - start_time).total_seconds()
                    }
                
                # 添加延迟
                time.sleep(test_execution_delay)
            
            # ========== 验证预期结果 ==========
            self._log_debug(f"验证预期结果: {test_case['expected']}")
            success, message = self._verify_expected(test_case['expected'])
            
            # ========== 更新后置状态 ==========
            self._update_post_conditions(case_id, success)
            
            if success:
                # 记录成功日志
                self._log_debug(f"用例 {case_id} 执行成功: {message}")
                return {
                    'status': 'PASS',
                    'message': message,
                    'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': (datetime.now() - start_time).total_seconds()
                }
            else:
                # 记录验证失败日志
                self._log_error(f"用例 {test_case['id']} 预期结果验证失败: {message}")
                # 失败时截图
                screenshot_manager.take_screenshot(f"{test_case['id']}_verify_failed")
                return {
                    'status': 'FAIL',
                    'message': f"预期结果验证失败: {message}",
                    'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': (datetime.now() - start_time).total_seconds()
                }
                
        except Exception as e:
            # 记录异常日志
            self._log_error(f"用例 {test_case['id']} 执行异常: {str(e)}")
            # 异常时截图
            screenshot_manager.take_screenshot(f"{test_case['id']}_exception")
            import traceback
            self._log_error(f"异常堆栈: {traceback.format_exc()}")
            return {
                'status': 'FAIL',
                'message': f"执行异常: {str(e)}",
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration': (datetime.now() - start_time).total_seconds()
            }
    
    def _parse_steps(self, steps_str):
        """解析测试步骤"""
        steps = []
        
        # 按<br>或换行分割步骤
        step_parts = re.split(r'<br\s*/?>|\n', steps_str)
        
        for part in step_parts:
            part = part.strip()
            if not part:
                continue
            
            # 移除步骤编号（如"1. "、"2. "等）
            step_text = re.sub(r'^\d+\.\s*', '', part)
            
            # 解析动作和目标
            action, target = self._parse_step_action(step_text)
            
            steps.append({
                'description': step_text,
                'action': action,
                'target': target
            })
        
        return steps
    
    def _parse_step_action(self, step_text):
        """解析步骤动作"""
        if '等待' in step_text:
            # 提取等待时间
            match = re.search(r'等待(\d+)秒?', step_text)
            if match:
                return ('wait', int(match.group(1)))
            return ('wait', 2)  # 默认等待2秒
        
        elif '点击' in step_text:
            # 提取点击目标
            # 先移除"按钮"后缀，避免干扰
            step_text_clean = step_text.replace('按钮', '').strip()
            
            # 特殊处理：如果包含"弹窗的"，直接提取整个目标
            if '弹窗的' in step_text_clean:
                # 提取"弹窗的"后面的内容
                match = re.search(r'弹窗的["“”\']?(.*?)["“”\']?$', step_text_clean)
                if match:
                    target = '弹窗的' + match.group(1).strip()
                    return ('click', target)
            
            # 尝试匹配引号内容
            match = re.search(r'点击["“”\']?(.*?)["“”\']?$', step_text_clean)
            if match:
                target = match.group(1).strip()
                # 如果target为空或只有引号，使用整个文本
                if not target or target in ['"', "'", '"', '"']:
                    target = step_text_clean.replace('点击', '').strip().strip('"').strip("'").strip('"').strip('"')
                return ('click', target)
            return ('click', step_text_clean.replace('点击', '').strip())
        
        elif '输入' in step_text:
            # 提取输入内容
            # 尝试匹配引号内容
            match = re.search(r'输入["“”\']?(.*?)["“”\']?$', step_text)
            if match:
                target = match.group(1).strip()
                # 如果target为空或只有特殊字符，使用"输入"后面的所有内容
                if not target or target in ['"', "'", '"', '"', '：', ':']:
                    target = step_text.replace('输入', '').strip().strip('"').strip("'").strip('"').strip('"').strip('：').strip(':')
                return ('input', target)
            # 如果没有引号，直接提取"输入"后面的内容
            target = step_text.replace('输入', '').strip().strip('：').strip(':')
            return ('input', target)
        
        elif '进入' in step_text:
            return ('navigate', step_text.replace('进入', '').strip())
        
        elif '切换到' in step_text:
            return ('switch', step_text.replace('切换到', '').strip())
        
        elif '选择' in step_text:
            return ('select', step_text.replace('选择', '').strip())
        
        elif '勾选' in step_text:
            # 提取勾选目标
            match = re.search(r'勾选["“”\']?(.*?)["“”\']?$', step_text)
            if match:
                target = match.group(1).strip()
                return ('click', target)
            return ('click', step_text.replace('勾选', '').strip())
        
        elif '返回' in step_text:
            return ('back', '')
        
        elif '退出' in step_text:
            return ('exit', '')
        
        elif '启动' in step_text or '打开' in step_text:
            # 启动App或打开App
            return ('launch', step_text)
        
        return ('action', step_text)
    
    def _execute_step(self, step):
        """执行单个步骤"""
        action = step['action']
        target = step['target']
        
        try:
            if action == 'wait':
                time.sleep(target)
                return True, f"等待 {target} 秒"
            
            elif action == 'click':
                return self._click_target(target)
            
            elif action == 'input':
                return self._input_text(target)
            
            elif action == 'navigate':
                return self._navigate_to(target)
            
            elif action == 'switch':
                return self._switch_to(target)
            
            elif action == 'select':
                return self._select_option(target)
            
            elif action == 'back':
                return self._go_back()
            
            elif action == 'exit':
                return self._exit_app()
            
            elif action == 'launch':
                return self._launch_app(target)
            
            else:
                # 默认尝试点击
                return self._click_target(target)
                
        except Exception as e:
            return False, str(e)
    
    def _click_target(self, target):
        """点击目标元素"""
        # 如果是登录按钮，先收起键盘
        if target == '登录':
            subprocess.run('adb shell input keyevent KEYCODE_BACK', shell=True, capture_output=True)
            time.sleep(0.5)
        
        # 尝试通过坐标映射查找
        coord_key = self._find_coordinate_key(target)
        
        if coord_key and coord_key in coordinates:
            self._tap_coords(coordinates[coord_key])
            return True, f"点击坐标 {coordinates[coord_key]}"
        
        # 尝试通过文本查找元素
        coords = self._find_element_by_text(target)
        if coords:
            self._tap_coords(coords)
            return True, f"点击文本 '{target}' 位置 {coords}"
        
        # 尝试通过关键字查找
        coords = self._find_element_by_keyword(target)
        if coords:
            self._tap_coords(coords)
            return True, f"点击关键字 '{target}' 位置 {coords}"
        
        return False, f"未找到元素: {target}"
    
    def _find_coordinate_key(self, target):
        """查找坐标映射键"""
        # 建立目标到坐标键的映射（按关键词长度降序排列，优先匹配长关键词）
        key_mappings = {
            # 内部账号弹窗按钮（优先匹配，因为用户用例步骤是"弹窗的取消/暂不登录"）
            '弹窗的取消按钮': 'tip_popup_cancel',
            '弹窗的暂不登录按钮': 'tip_popup_no_login',
            '弹窗的取消': 'tip_popup_cancel',
            '弹窗的暂不登录': 'tip_popup_no_login',
            '弹窗取消按钮': 'tip_popup_cancel',
            '弹窗暂不登录按钮': 'tip_popup_no_login',
            '弹窗取消': 'tip_popup_cancel',
            '弹窗暂不登录': 'tip_popup_no_login',

            # 授权弹窗按钮
            '弹窗的"同意"': 'auth_agree',
            '弹窗的"取消"': 'auth_cancel',
            '弹窗"暂不登录"': 'auth_agree',
            '弹窗"取消"': 'auth_cancel',
            '弹窗的同意': 'auth_agree',
            '弹窗同意': 'auth_agree',
            '授权同意': 'auth_agree',
            '授权取消': 'auth_cancel',
            
            # 隐私协议页按钮
            '隐私协议同意': 'privacy_agree',
            '隐私页同意': 'privacy_agree',
            '同意': 'privacy_agree',
            '拒绝': 'privacy_disagree',
            
            # 引导页按钮
            '开始使用': 'guide_start',
            
            # 登录页按钮
            '短信验证码登录': 'sms_login',
            '登录': 'login_button',
            '获取验证码': 'get_code',
            '暂不登录': 'no_login',
            '密码登录': 'password_login',
            '同意协议': 'agreement_checkbox',
            
            # 底部导航
            '首页': 'nav_home',
            '订单': 'nav_order',
            '商品': 'nav_goods',
            '我的': 'nav_mine',
            
            # 分类标签
            '设备': 'category_equipment',
            '建材': 'category_material',
            '人才': 'category_talent',
            '服务': 'category_service',
            '买设备': 'equipment_buy',
            '租设备': 'equipment_rent',
            '买建材': 'material_buy',
            '租建材': 'material_rent',
            '找人才': 'talent_find',
            '找班组': 'talent_team',
            '全部': 'service_all',
            '设计服务': 'service_design',
            '信息服务': 'service_info',
            'BIM服务': 'service_bim',
            '预算造价': 'service_budget',
            
            # 搜索和筛选
            '搜索': 'search_button',
            '搜索框': 'search_input',
            '全国': 'region_filter',
            '销量': 'sales_sort',
            '筛选': 'filter_button',
            
            # 订单状态
            '待确认': 'order_pending',
            '进行中': 'order_processing',
            '待评价': 'order_review',
            '已完成': 'order_completed',
            '订单筛选': 'order_filter_button',
            
            # 我的页面
            '收货地址': 'mine_address',
            '公司资质': 'mine_qualification',
            '意见反馈': 'mine_feedback',
            '系统设置': 'mine_settings',
            '关于我们': 'mine_about',
            '退出登录': 'settings_logout',
            '成员管理': 'mine_member_manage',
            '全部订单': 'home_all_orders',
            '更多消息': 'home_more_messages',
            '电话咨询': 'phone_call',
            
            # 其他
            '返回': 'back_button',
            '确定': 'logout_confirm_ok',
            '取消': 'logout_confirm_cancel',
        }
        
        # 1. 精确匹配
        if target in key_mappings:
            return key_mappings[target]
        
        # 2. 按关键词长度降序匹配（优先匹配长关键词，避免短关键词误匹配）
        sorted_keywords = sorted(key_mappings.keys(), key=len, reverse=True)
        for keyword in sorted_keywords:
            if keyword in target:
                return key_mappings[keyword]
        
        return None
    
    def _find_element_by_text(self, text):
        """通过文本查找元素坐标"""
        # 获取当前界面XML
        xml_content = self._dump_ui_hierarchy()
        
        if not xml_content:
            return None
        
        # 使用正则查找包含该文本的节点
        pattern = rf'<node[^>]*text="([^"]*{re.escape(text)}[^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        matches = re.findall(pattern, xml_content)
        
        if matches:
            # 取第一个匹配的元素中心坐标
            _, left, top, right, bottom = matches[0]
            x = (int(left) + int(right)) // 2
            y = (int(top) + int(bottom)) // 2
            return [x, y]
        
        return None
    
    def _find_element_by_keyword(self, keyword):
        """通过关键字查找元素坐标"""
        # 获取当前界面XML
        xml_content = self._dump_ui_hierarchy()
        
        if not xml_content:
            return None
        
        # 尝试多个可能的文本
        possible_texts = [keyword]
        
        # 添加一些常见变体
        if '页面' in keyword:
            possible_texts.append(keyword.replace('页面', ''))
        if '按钮' in keyword:
            possible_texts.append(keyword.replace('按钮', ''))
        
        for text in possible_texts:
            coords = self._find_element_by_text(text)
            if coords:
                return coords
        
        return None
    
    def _input_text(self, text):
        """输入文本"""
        xml_content = self._dump_ui_hierarchy()
        # 查找所有EditText或输入框
        pattern = r'<node[^>]*class="android\.widget\.EditText"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        matches = re.findall(pattern, xml_content)
        
        if not matches:
            self._log_error("未找到输入框")
            return False, "未找到输入框"
        
        # 根据输入内容选择正确的输入框
        # 如果是手机号（11位数字），选择第一个输入框
        # 如果是验证码（6位数字），选择第二个输入框
        clean_text = ''.join([c for c in text if c.isdigit()])
        input_index = 0
        if len(clean_text) == 6:
            # 6位验证码，选择第二个输入框
            input_index = 1 if len(matches) > 1 else 0
        
        if input_index < len(matches):
            left, top, right, bottom = matches[input_index]
            x = (int(left) + int(right)) // 2
            y = (int(top) + int(bottom)) // 2
            self._tap_coords([x, y])
        else:
            # 如果没有第二个输入框，使用第一个
            left, top, right, bottom = matches[0]
            x = (int(left) + int(right)) // 2
            y = (int(top) + int(bottom)) // 2
            self._tap_coords([x, y])

        time.sleep(1)
        
        # 清除输入框内容 - 先全选再删除
        subprocess.run('adb shell input keyevent KEYCODE_CTRL_A', shell=True, capture_output=True)
        time.sleep(0.2)
        subprocess.run('adb shell input keyevent KEYCODE_DEL', shell=True, capture_output=True)
        time.sleep(0.5)
        
        # 输入文本
        # 清理文本，移除中文冒号、英文冒号等特殊字符，只保留数字
        clean_text = ''.join([c for c in text if c.isdigit()])
        print(f"        输入内容: 原始='{text}', 清理后='{clean_text}', 输入框索引={input_index}")
        self._log_debug(f"输入文本: 原始='{text}', 清理后='{clean_text}', 输入框索引={input_index}")
        
        # 使用按键事件输入，模拟真实键盘输入
        keycode_map = {
            '0': 'KEYCODE_0',
            '1': 'KEYCODE_1',
            '2': 'KEYCODE_2',
            '3': 'KEYCODE_3',
            '4': 'KEYCODE_4',
            '5': 'KEYCODE_5',
            '6': 'KEYCODE_6',
            '7': 'KEYCODE_7',
            '8': 'KEYCODE_8',
            '9': 'KEYCODE_9',
        }
        
        # 对于手机号（11位），使用特殊方法避免格式化
        if len(clean_text) == 11:
            # 先输入前10位
            for i in range(10):
                char = clean_text[i]
                if char in keycode_map:
                    subprocess.run(f'adb shell input keyevent {keycode_map[char]}', shell=True, capture_output=True)
                    time.sleep(0.05)
            
            # 输入最后一位后立即按回车键
            last_char = clean_text[-1]
            if last_char in keycode_map:
                subprocess.run(f'adb shell input keyevent {keycode_map[last_char]}', shell=True, capture_output=True)
            
            # 立即按回车键完成输入
            time.sleep(0.1)
            subprocess.run('adb shell input keyevent KEYCODE_ENTER', shell=True, capture_output=True)
        else:
            # 非手机号（如验证码）直接输入
            for char in clean_text:
                if char in keycode_map:
                    subprocess.run(f'adb shell input keyevent {keycode_map[char]}', shell=True, capture_output=True)
                    time.sleep(0.05)
        
        return True, f"输入文本: {text}"
    
    def _navigate_to(self, target):
        """导航到指定页面"""
        # 尝试通过底部导航
        nav_mappings = {
            '首页': 'nav_home',
            '订单': 'nav_order',
            '商品': 'nav_goods',
            '我的': 'nav_mine',
            '个人中心': 'nav_mine',
        }
        
        if target in nav_mappings:
            self._tap_coords(coordinates[nav_mappings[target]])
            return True, f"导航到 {target}"
        
        # 默认尝试点击
        return self._click_target(target)
    
    def _switch_to(self, target):
        """切换到指定视图"""
        # 切换分类标签
        category_mappings = {
            '设备': 'category_equipment',
            '建材': 'category_material',
            '人才': 'category_talent',
            '服务': 'category_service',
            '买设备': 'equipment_buy',
            '租设备': 'equipment_rent',
            '买建材': 'material_buy',
            '租建材': 'material_rent',
            '找人才': 'talent_find',
            '找班组': 'talent_team',
        }
        
        if target in category_mappings:
            self._tap_coords(coordinates[category_mappings[target]])
            return True, f"切换到 {target}"
        
        # 切换底部导航
        return self._navigate_to(target)
    
    def _select_option(self, target):
        """选择选项"""
        # 尝试通过文本查找并点击
        coords = self._find_element_by_text(target)
        if coords:
            self._tap_coords(coords)
            return True, f"选择 {target}"
        
        return False, f"未找到选项: {target}"
    
    def _go_back(self):
        """返回上一页"""
        # 先尝试点击返回按钮
        if 'back_button' in coordinates:
            self._tap_coords(coordinates['back_button'])
        else:
            # 使用返回键
            subprocess.run('adb shell input keyevent KEYCODE_BACK', shell=True, capture_output=True)
        
        return True, "返回上一页"
    
    def _exit_app(self):
        """退出App"""
        subprocess.run('adb shell input keyevent KEYCODE_HOME', shell=True, capture_output=True)
        return True, "退出App"
    
    def _launch_app(self, target):
        """启动App"""
        from config import app_package, app_activity
        
        # 使用am start启动应用
        cmd = f'adb shell am start -n {app_package}/{app_activity}'
        subprocess.run(cmd, shell=True, capture_output=True)
        time.sleep(3)  # 等待App启动
        
        # 重置状态
        self._reset_app_state()
        
        return True, "启动App成功"
    
    def _tap_coords(self, coords):
        """点击坐标"""
        x, y = coords
        print(f"    点击坐标: ({x}, {y})")
        cmd = f'adb shell input tap {x} {y}'
        subprocess.run(cmd, shell=True, capture_output=True)
        time.sleep(0.5)
    
    def _dump_ui_hierarchy(self):
        """获取当前界面UI层次结构"""
        try:
            # 使用项目目录存储临时文件
            import tempfile
            temp_dir = tempfile.gettempdir()
            local_path = f"{temp_dir}/ui_dump.xml"
            
            # 导出XML
            cmd = 'adb shell uiautomator dump /sdcard/ui_dump.xml'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=adb_timeout)
            
            # 拉取XML到临时目录
            cmd = f'adb pull /sdcard/ui_dump.xml "{local_path}"'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=adb_timeout)
            
            # 读取XML内容
            with open(local_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            self._log_error(f"获取UI层次结构失败: {str(e)}")
            return None
    
    def _verify_expected(self, expected):
        """验证预期结果"""
        # 获取当前界面文本
        xml_content = self._dump_ui_hierarchy()
        
        if not xml_content:
            return False, "无法获取界面内容"
        
        # 获取所有界面文本
        texts = re.findall(r'text="([^"]+)"', xml_content)
        all_text = ' '.join(texts)
        
        # 记录当前界面所有文本用于调试
        self._log_debug(f"当前界面文本内容: {texts[:20]}...")  # 只记录前20个
        
        # 定义预期结果关键字映射（支持Unicode编码字符）
        expected_keywords_map = {
            "登录成功,显示客户信息": ["首页", "订单", "商品", "我的", "棣栭", "璁㈠崟", "鍟嗗搧", "鎴戠殑"],
            "登录成功,显示底部导航栏（首页、订单、商品、我的）": ["首页", "订单", "商品", "我的", "棣栭", "璁㈠崟", "鍟嗗搧", "鎴戠殑"],
            "进入验证码登录界面": ["请输入手机号", "验证码"],
            "进入游客访问界面，有立即登录,查看更多 按钮展示": ["首页", "订单", "商品", "我的", "立即登录", "查看更多", "棣栭", "璁㈠崟", "鍟嗗搧"],
            "退出App，回到手机桌面": [],  # 空列表表示无需验证（App已退出）
            "进入登录页面，显示\"暂不登录\"、\"本机号码一键登录\"、\"短信验证码登录\"按钮": ["暂不登录", "本机号码一键登录", "短信验证码登录"],
            "进入首页访客模式，显示底部导航栏（订单、商品、我的）": ["首页", "订单", "商品", "我的", "棣栭", "璁㈠崟", "鍟嗗搧", "鎴戠殑"],
            "退出App": [],
        }
        
        # 根据预期结果关键字验证
        if expected in expected_keywords_map:
            keywords = expected_keywords_map[expected]
            
            if not keywords:  # 空列表表示无需验证（如退出App）
                return True, "无需验证"
            
            # 检查是否包含至少一个预期关键字
            found_keywords = [kw for kw in keywords if kw in all_text]
            
            if found_keywords:
                return True, f"找到预期关键字: {', '.join(found_keywords)}"
            else:
                return False, f"未找到预期关键字: {', '.join(keywords)}。当前界面文本: {all_text[:200]}"
        
        else:
            # 直接检查预期文本是否存在
            if expected in all_text:
                return True, f"找到预期文本: {expected}"
            
            # 尝试部分匹配
            expected_parts = expected.replace('、', ' ').replace('，', ' ').split()
            matched_parts = [part for part in expected_parts if part in all_text]
            
            if len(matched_parts) >= len(expected_parts) * 0.7:
                return True, f"部分匹配成功: {', '.join(matched_parts)}"
            
            return False, f"未找到预期内容: {expected}"
    
    def _verify_step_result(self, step, step_number):
        """验证步骤执行结果（关键步骤）"""
        action = step['action']
        target = step['target']
        
        # 只有点击关键按钮后才验证
        if action != 'click':
            return True, "无需验证"
        
        # 定义关键按钮点击后的验证规则（支持Unicode编码字符）
        verification_rules = {
            # 点击后应该出现的关键字
            '同意': ['本机号码一键登录', '短信验证码登录', '开始使用'],  # 隐私协议同意后进入登录页，或仍在引导页
            '开始使用': ['同意', '本机号码一键登录'],  # 点击开始使用后出现隐私协议或登录页
            '本机号码一键登录': ['弹窗', '温馨提示', '中国联通', '认证服务协议', '欢迎来到'],  # 点击后出现授权弹窗
            '短信验证码登录': ['请输入手机号', '验证码'],  # 点击后进入短信登录页
            '登录': ['温馨提示', '首页', '订单', '暂不登录', '棣栭', '璁㈠崟', '鍟嗗搧', '鎴戠殑'],  # 登录后可能的结果（包括失败）
            '弹窗的同意': ['温馨提示', '内部账号', '暂不登录'],  # 授权弹窗同意后出现内部账号弹窗或登录页
            '弹窗的取消': ['请输入手机号', '短信'],  # 弹窗取消后回到登录页
            '弹窗的暂不登录': ['首页', '订单', '商品', '棣栭', '璁㈠崟', '鍟嗗搧'],  # 暂不登录后进入首页
        }
        
        # 检查是否有验证规则
        if target in verification_rules:
            expected_keywords = verification_rules[target]
            
            # 获取当前界面文本
            xml_content = self._dump_ui_hierarchy()
            if not xml_content:
                return False, "无法获取界面内容进行验证"
            
            texts = re.findall(r'text="([^"]+)"', xml_content)
            all_text = ' '.join(texts)
            
            # 检查是否包含任意一个预期关键字
            found_keyword = None
            for kw in expected_keywords:
                if kw in all_text:
                    found_keyword = kw
                    break
            
            if found_keyword:
                self._log_debug(f"步骤 {step_number} 验证通过: 找到关键字 '{found_keyword}'")
                return True, f"验证通过: 找到关键字 '{found_keyword}'"
            else:
                error_msg = f"步骤 {step_number} 验证失败: 点击'{target}'后未找到预期关键字[{', '.join(expected_keywords)}]，当前界面文本: {all_text[:150]}..."
                self._log_error(error_msg)
                return False, error_msg
        
        return True, "无需验证"