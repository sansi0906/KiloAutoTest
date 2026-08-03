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

    def test_login_missing_login_type(self):
        """缺少 loginType 字段，应返回失败"""
        response = self.client.login(
            username=self.config["username"],
            password=self.config["password"],
            login_type=None,
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)

    @pytest.mark.backend_bug
    def test_login_missing_sms_code(self):
        """缺少 smsCode 字段，密码登录模式下后端未校验 smsCode"""
        response = self.client.post("/sys/login", json={
            "username": self.config["username"],
            "password": self.config["password"],
            "loginType": self.config.get("LOGIN_TYPE", 1),
            "webType": self.config.get("WEB_TYPE", 0),
            "smsCode": None,
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 密码登录模式下 smsCode 应为非必填，但 OpenAPI 标记为必填
        # 后端实际接受 null smsCode 并返回成功
        self.assert_login_success(data)

    def test_login_missing_web_type(self):
        """缺少 webType 字段，应返回失败"""
        response = self.client.login(
            username=self.config["username"],
            password=self.config["password"],
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)