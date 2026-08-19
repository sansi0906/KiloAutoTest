"""
test_base.py - 服务定价配置管理模块测试基类
==================================================
提供服务定价配置管理模块的通用测试设置和辅助方法
"""

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "pricing_module"
    _module_desc = "服务定价配置管理模块"

    def _delete_test_data(self, item_id):
        """删除测试数据（pricing 没有 delete 接口，这里只是占位）"""
        pass
