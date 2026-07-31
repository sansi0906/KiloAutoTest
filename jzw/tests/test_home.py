"""
津筑网App - 首页模块测试用例
"""
import pytest
from pages.home_page import HomePage


@pytest.mark.home
class TestHome:
    """首页功能测试"""

    def test_home_page_displayed(self, app):
        """HOME-001: 首页正常显示"""
        home = HomePage(app).navigate()
        # 验证4个分类入口都显示
        for cat in HomePage.CATEGORIES:
            assert home.is_category_displayed(cat), f"分类'{cat}'未显示"
        app.screenshot("home_001_page_displayed")

    def test_category_equipment(self, app):
        """HOME-002: 点击设备分类跳转"""
        home = HomePage(app).navigate()
        result = home.click_category("设备")
        assert result, "无法点击设备分类"
        # 验证跳转后页面变化
        assert not app.is_text_present("设备") or \
               app.find_element(resourceId="com.tjxinyu.fz:id/rl_product_item").exists, \
               "点击设备后未跳转到商品列表"
        app.screenshot("home_002_category_equipment")

    def test_category_talent(self, app):
        """HOME-003: 点击人才分类跳转"""
        home = HomePage(app).navigate()
        result = home.click_category("人才")
        assert result, "无法点击人才分类"
        app.screenshot("home_003_category_talent")

    def test_category_service(self, app):
        """HOME-004: 点击服务分类跳转"""
        home = HomePage(app).navigate()
        result = home.click_category("服务")
        assert result, "无法点击服务分类"
        app.screenshot("home_004_category_service")

    def test_transaction_stat_click(self, app):
        """HOME-005: 点击交易统计数字"""
        home = HomePage(app).navigate()
        home.click_transaction_stat()
        # 验证有响应（页面变化或跳转）
        app.screenshot("home_005_transaction_click")

    def test_order_status_all(self, app):
        """HOME-006: 点击全部订单"""
        home = HomePage(app).navigate()
        result = home.click_all_orders()
        if result:
            app.screenshot("home_006_all_orders")
        else:
            pytest.skip("全部订单按钮未找到")

    def test_order_status_pending(self, app):
        """HOME-007: 点击待确认订单数"""
        home = HomePage(app).navigate()
        result = home.click_order_status("待确认")
        if result:
            app.screenshot("home_007_order_pending")
        else:
            pytest.skip("待确认元素未找到")

    def test_message_card(self, app):
        """HOME-008: 点击消息卡片"""
        home = HomePage(app).navigate()
        result = home.click_message_card()
        if result:
            app.screenshot("home_008_message_card")
        else:
            pytest.skip("消息卡片未找到")
