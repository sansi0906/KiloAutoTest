"""
津筑网App - 系统设置测试用例
"""
import pytest
import time
from pages.settings_page import SettingsPage
from pages.mine_page import MinePage


@pytest.mark.settings
class TestSettings:
    """系统设置页功能测试"""

    def test_settings_page_displayed(self, app):
        """SETTING-001: 系统设置页正常显示"""
        settings = SettingsPage(app).navigate()
        assert settings is not None, "无法进入系统设置页"
        app.screenshot("settings_001_page_displayed")

    def test_logout_button(self, app):
        """SETTING-002: 退出登录按钮"""
        settings = SettingsPage(app).navigate()
        assert settings is not None, "无法进入系统设置页"
        result = settings.click_logout()
        assert result, "退出登录按钮未找到"
        # 验证弹窗显示
        assert settings.is_logout_dialog_displayed(), "退出登录弹窗未显示"
        app.screenshot("settings_002_logout_dialog")

    def test_logout_cancel(self, app):
        """SETTING-003: 取消退出登录"""
        settings = SettingsPage(app).navigate()
        assert settings is not None
        settings.click_logout()
        result = settings.cancel_logout()
        assert result, "无法取消退出登录"
        # 验证弹窗已关闭
        assert not settings.is_logout_dialog_displayed(), "弹窗未关闭"
        app.screenshot("settings_003_logout_cancelled")

    def test_cancel_account_button(self, app):
        """SETTING-004: 注销账户按钮"""
        settings = SettingsPage(app).navigate()
        assert settings is not None
        result = settings.click_cancel_account()
        assert result, "注销账户按钮未找到"
        # 验证弹窗显示
        assert settings.is_cancel_account_dialog_displayed(), "注销账户弹窗未显示"
        app.screenshot("settings_004_cancel_account_dialog")

    def test_cancel_account_cancel(self, app):
        """SETTING-005: 取消注销账户"""
        settings = SettingsPage(app).navigate()
        assert settings is not None
        settings.click_cancel_account()
        result = settings.cancel_cancel_account()
        assert result, "无法取消注销账户"
        assert not settings.is_cancel_account_dialog_displayed(), "弹窗未关闭"
        app.screenshot("settings_005_cancel_account_cancelled")
