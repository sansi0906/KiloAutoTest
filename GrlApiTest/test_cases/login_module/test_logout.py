"""
test_logout.py - 用户登出接口测试
======================================
覆盖登出模块的场景：
- 有效 Token 登出成功
- 无 Token 登出失败
- 无效 Token 登出失败
- 空 Token 登出
- 登出后重新登录的完整生命周期
"""

from .test_base import TestBase


class TestLogout(TestBase):
    def test_logout_with_valid_token(self):
        """使用有效 Token 登出，应返回成功"""
        token = self.login()
        self.client.set_token(token)
        response = self.client.logout()
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_logout_without_token(self):
        """无 Token 登出，应返回失败"""
        response = self.client.logout()
        assert response.status_code == 200
        data = response.json()
        self.assert_save_failure(data)

    def test_logout_with_invalid_token(self):
        """使用无效 Token 登出，应返回失败"""
        self.client.set_token("invalid_token_12345")
        response = self.client.logout()
        assert response.status_code == 200
        data = response.json()
        self.assert_save_failure(data)

    def test_logout_with_empty_token(self):
        """使用空 Token 登出，应返回失败"""
        self.client.set_token("")
        response = self.client.logout()
        assert response.status_code == 200

    def test_logout_then_relogin(self):
        """登出后重新登录，验证完整生命周期"""
        # 1. 登录获取 Token
        token = self.login()
        self.client.set_token(token)

        # 2. 登出
        logout_response = self.client.logout()
        assert logout_response.status_code == 200
        logout_data = logout_response.json()
        self.assert_save_success(logout_data)

        # 3. 重新登录
        login_response = self.client.login(
            username=self.config["username"],
            password=self.config["password"],
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        self.assert_login_success(login_data)