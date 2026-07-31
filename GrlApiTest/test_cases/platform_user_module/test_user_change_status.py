"""
test_user_change_status.py - 平台用户修改状态接口测试
=============================================
覆盖平台用户管理模块的修改状态接口场景：
- 禁用已启用的用户
- 启用已禁用的用户
- 修改不存在的用户状态
"""

import pytest

from .test_base import TestBase


class TestUserChangeStatus(TestBase):
    def test_disable_existing_user(self):
        """禁用已启用的用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user(status=1)

        response = self.client.change_user_status(user_id=user_id, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_enable_existing_user(self):
        """启用已禁用的用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user(status=0)

        response = self.client.change_user_status(user_id=user_id, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_non_existing_user(self):
        """修改不存在的用户状态，按正常逻辑应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.change_user_status(user_id=999999, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
