"""
test_base.py - 角色管理模块测试基类
===================================================
提供角色管理模块的通用测试设置和辅助方法
"""

import time
import random

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "role_management_module"
    _module_desc = "角色管理模块"

    def _unique_role_name(self):
        """生成唯一的角色名称，格式：测试角色+秒级时间戳"""
        return f"测试角色{int(time.time())}"

    def _unique_role_remark(self):
        """生成唯一的角色备注，格式：备注+随机数"""
        return f"备注{random.randint(1000, 9999)}"

    def _create_role(self, role_name=None, status=1, role_remark=None):
        """创建角色并通过分页查询获取角色ID

        Returns:
            (role_id, role_name, role_remark) 元组
        """
        role_name = role_name or self._unique_role_name()
        role_remark = role_remark or self._unique_role_remark()
        role_id, _ = self._create_and_get_id(
            create_fn=lambda: self.client.save_role(
                role_name=role_name,
                status=status,
                role_remark=role_remark,
            ),
            query_fn=lambda: self.client.page_roles(page_num=1, page_size=10, role_name=role_name),
            match_key="roleName",
            match_value=role_name,
        )
        return role_id, role_name, role_remark

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.delete_role(role_id=item_id)
