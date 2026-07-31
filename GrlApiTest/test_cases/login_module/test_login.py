"""
test_login.py - 用户登录接口测试
=======================================
覆盖用户登录模块的核心场景：
- 正常登录
- 错误用户名
- 错误密码
- 空用户名 / 空密码
"""

import pytest

from .test_base import TestBase


class TestLogin(TestBase):
    @pytest.mark.smoke
    def test_login_success(self):
        """使用正确凭证登录，应返回成功和 Token"""
        response = self.client.login(
            username=self.config["username"],
            password=self.config["password"],
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_success(data)

    def test_login_invalid_username(self):
        """使用不存在的用户名登录，应返回失败"""
        response = self.client.login(
            username="wrong_user",
            password=self.config["password"],
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)

    def test_login_invalid_password(self):
        """使用错误密码登录，应返回失败"""
        response = self.client.login(
            username=self.config["username"],
            password="wrong_pass",
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)

    def test_login_empty_username(self):
        """使用空用户名登录，应返回失败"""
        response = self.client.login(
            username="",
            password=self.config["password"],
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)

    def test_login_empty_password(self):
        """使用空密码登录，应返回失败"""
        response = self.client.login(
            username=self.config["username"],
            password="",
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)