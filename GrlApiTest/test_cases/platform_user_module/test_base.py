"""
test_base.py - 平台用户管理模块测试基类
==================================================
提供平台用户管理模块的通用测试设置和辅助方法
"""

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "platform_user_module"
    _module_desc = "平台用户管理模块"

    def _create_user(self, user_name=None, real_name=None, sex=1, role_group_id=5, status=1):
        """创建用户并通过分页查询获取用户ID

        Returns:
            (user_id, user_name, real_name) 元组
        """
        user_name = user_name or self._unique_user_name()
        real_name = real_name or self._unique_real_name()
        user_id, _ = self._create_and_get_id(
            create_fn=lambda: self.client.save_platform_user(
                user_name=user_name,
                real_name=real_name,
                sex=sex,
                role_group_id=role_group_id,
                status=status,
            ),
            query_fn=lambda: self.client.page_users(page_num=1, page_size=10, user_name=user_name),
            match_key="userName",
            match_value=user_name,
        )
        return user_id, user_name, real_name

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.delete_user(user_id=item_id)
