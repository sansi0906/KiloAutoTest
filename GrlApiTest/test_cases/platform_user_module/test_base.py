"""
test_base.py - 平台用户管理模块测试基类
===================================================
提供平台用户管理模块的通用测试设置和辅助方法
"""

import time
import random

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "platform_user_module"
    _module_desc = "平台用户管理模块"

    def _unique_real_name(self):
        """生成唯一的真实姓名，格式：测试用户+秒级时间戳"""
        return f"测试用户{int(time.time())}"

    def _unique_user_name(self):
        """生成唯一的用户名（174开头的11位纯数字手机号）"""
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    def _create_user(self, user_name=None, real_name=None, sex=1, role_group_id=5, status=1):
        """创建用户并通过分页查询获取用户ID

        Returns:
            (user_id, user_name, real_name) 元组
        """
        user_name = user_name or self._unique_user_name()
        real_name = real_name or self._unique_real_name()
        response = self.client.save_platform_user(
            user_name=user_name,
            real_name=real_name,
            sex=sex,
            role_group_id=role_group_id,
            status=status,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        page_resp = self.client.page_users(page_num=1, page_size=10, user_name=user_name)
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        user_id = None
        for record in records:
            if record.get("userName") == user_name:
                user_id = record.get("id")
                break
        assert user_id, f"User not found after creation: {page_data}"
        self._created_ids.append(user_id)
        return user_id, user_name, real_name

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.delete_user(user_id=item_id)
