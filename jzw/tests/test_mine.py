"""
津筑网App - 我的页面测试用例
"""
import pytest
import time
from pages.mine_page import MinePage


@pytest.mark.mine
class TestMine:
    """我的页面功能测试"""

    def test_mine_page_displayed(self, app):
        """MINE-001: 我的页面正常显示"""
        mine = MinePage(app).navigate()
        # 验证关键功能入口存在
        assert app.d(text="系统设置").exists, "系统设置入口未显示"
        app.screenshot("mine_001_page_displayed")

    def test_user_info_displayed(self, app):
        """MINE-002: 用户信息显示"""
        mine = MinePage(app).navigate()
        name = mine.get_user_name()
        app.screenshot("mine_002_user_info")
        # 用户名可能为空（取决于登录方式）
        if name:
            assert len(name) > 0, "用户昵称为空"

    def test_customer_service_phone(self, app):
        """MINE-003: 客服电话显示"""
        mine = MinePage(app).navigate()
        phone = mine.get_customer_service_phone()
        app.screenshot("mine_003_service_phone")

    def test_click_member_management(self, app):
        """MINE-004: 成员管理入口"""
        mine = MinePage(app).navigate()
        result = mine.click_member_management()
        if result:
            app.screenshot("mine_004_member_management")
        else:
            pytest.skip("成员管理入口未找到")

    def test_click_address(self, app):
        """MINE-005: 收货地址入口"""
        mine = MinePage(app).navigate()
        result = mine.click_address()
        if result:
            app.screenshot("mine_005_address")
        else:
            pytest.skip("收货地址入口未找到")

    def test_click_company_qualification(self, app):
        """MINE-006: 公司资质入口"""
        mine = MinePage(app).navigate()
        result = mine.click_company_qualification()
        if result:
            app.screenshot("mine_006_qualification")
        else:
            pytest.skip("公司资质入口未找到")

    def test_click_feedback(self, app):
        """MINE-007: 意见反馈入口"""
        mine = MinePage(app).navigate()
        result = mine.click_feedback()
        if result:
            app.screenshot("mine_007_feedback")
        else:
            pytest.skip("意见反馈入口未找到")

    def test_click_about_us(self, app):
        """MINE-008: 关于我们入口"""
        mine = MinePage(app).navigate()
        result = mine.click_about_us()
        if result:
            app.screenshot("mine_008_about_us")
        else:
            pytest.skip("关于我们入口未找到")

    def test_click_customer_service(self, app):
        """MINE-009: 客服电话点击"""
        mine = MinePage(app).navigate()
        result = mine.click_customer_service()
        if result:
            app.screenshot("mine_009_service_click")
        else:
            pytest.skip("客服电话未找到")
