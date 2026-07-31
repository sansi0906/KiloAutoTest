"""
test_user_detail.py - 平台用户详情接口测试
============================================
覆盖平台用户管理模块的详情接口场景：
- 获取存在的用户详情
- 获取不存在的用户详情
"""

import pytest

from .test_base import TestBase


class TestUserDetail(TestBase):
    def test_detail_existing_user(self):
        """获取已存在的用户详情，应返回成功并包含完整用户信息"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()

        response = self.client.get_user_detail(user_id=user_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        user_data = data.get("data", {})
        assert user_data.get("id") == str(user_id)
        assert user_data.get("userName") == user_name
        assert user_data.get("realName") == real_name

    def test_detail_non_existing_user(self):
        """获取不存在的用户详情，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.get_user_detail(user_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
