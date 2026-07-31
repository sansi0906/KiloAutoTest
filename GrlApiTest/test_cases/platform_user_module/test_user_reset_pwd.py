"""
test_user_reset_pwd.py - 平台用户重置密码接口测试
======================================================
覆盖平台用户管理模块的重置密码接口场景：
- 重置已知用户密码成功
- 使用不存在的用户ID重置密码
- 使用无效用户ID（0）重置密码
"""

import time
import random

import pytest

from .test_base import TestBase


class TestUserResetPwd(TestBase):
    def test_reset_pwd_success(self):
        """重置已知用户密码，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, _, _ = self._create_user()

        response = self.client.reset_pwd(user_id=user_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_reset_pwd_invalid_user_id(self):
        """使用不存在的用户ID重置密码，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.reset_pwd(user_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_reset_pwd_zero_user_id(self):
        """使用用户ID为0重置密码，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.reset_pwd(user_id=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)