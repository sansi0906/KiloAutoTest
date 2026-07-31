"""
test_base.py - 登录模块测试基类
===================================================
提供登录模块的通用测试设置和辅助方法
"""

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "login_module"
    _module_desc = "登录模块"
