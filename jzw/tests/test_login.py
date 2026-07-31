"""
津筑网App - 登录模块测试用例
"""
import pytest
from pages.login_page import LoginPage


@pytest.mark.login
class TestLogin:
    """登录功能测试"""

    # 测试账号
    PHONE = "17445146553"
    CODE = "000000"

    def test_app_launch(self, app):
        """LOGIN-001: App正常启动"""
        # 验证App已在前台运行
        assert app.dm.is_app_foreground(), "App未在前台运行"
        app.screenshot("login_001_app_launched")

    def test_login_page_elements(self, app):
        """LOGIN-002: 登录页元素验证"""
        login = LoginPage(app)
        # 验证手机号输入框存在
        assert app.is_text_present("登录") or \
               app.find_element(resourceId="com.tjxinyu.fz:id/et_phone").exists, \
               "登录页未正确显示"
        app.screenshot("login_002_page_elements")

    def test_phone_input(self, app):
        """LOGIN-003: 手机号输入验证"""
        login = LoginPage(app)
        # 输入手机号
        result = login.input_phone(self.PHONE)
        assert result, "无法输入手机号"
        # 验证输入内容正确
        el = app.find_element(resourceId="com.tjxinyu.fz:id/et_phone")
        if el.exists:
            actual = el.get_text()
            assert actual == self.PHONE, f"输入的手机号不匹配: 期望={self.PHONE}, 实际={actual}"
        app.screenshot("login_003_phone_input")

    def test_code_login(self, app):
        """LOGIN-004: 验证码登录完整流程"""
        login = LoginPage(app)
        # 执行验证码登录
        result = login.login_with_code(self.PHONE, self.CODE)
        assert result, "登录流程执行失败"
        # 验证登录成功
        assert login.is_login_success(), "登录后未进入首页"
        app.screenshot("login_004_login_success")
