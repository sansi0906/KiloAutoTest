"""
津筑网App - 订单模块测试用例
"""
import pytest
import time
from pages.orders_page import OrdersPage, OrderDetailPage


@pytest.mark.orders
class TestOrders:
    """订单页功能测试"""

    def test_orders_page_displayed(self, app):
        """ORDERS-001: 订单页正常显示"""
        orders = OrdersPage(app).navigate()
        # 验证5个状态Tab显示
        for state in OrdersPage.STATES:
            assert app.d(text=state).exists, f"状态Tab'{state}'未显示"
        app.screenshot("orders_001_page_displayed")

    def test_switch_to_all(self, app):
        """ORDERS-002: 切换到全部订单"""
        orders = OrdersPage(app).navigate()
        result = orders.switch_state("全部")
        assert result, "无法切换到全部"
        app.screenshot("orders_002_all")

    def test_switch_to_pending(self, app):
        """ORDERS-003: 切换到待确认"""
        orders = OrdersPage(app).navigate()
        result = orders.switch_state("待确认")
        assert result, "无法切换到待确认"
        app.screenshot("orders_003_pending")

    def test_switch_to_in_progress(self, app):
        """ORDERS-004: 切换到进行中"""
        orders = OrdersPage(app).navigate()
        result = orders.switch_state("进行中")
        assert result, "无法切换到进行中"
        app.screenshot("orders_004_in_progress")

    def test_switch_to_to_review(self, app):
        """ORDERS-005: 切换到待评价"""
        orders = OrdersPage(app).navigate()
        result = orders.switch_state("待评价")
        assert result, "无法切换到待评价"
        app.screenshot("orders_005_to_review")

    def test_switch_to_completed(self, app):
        """ORDERS-006: 切换到已完成"""
        orders = OrdersPage(app).navigate()
        result = orders.switch_state("已完成")
        assert result, "无法切换到已完成"
        app.screenshot("orders_006_completed")

    def test_click_order_card(self, app):
        """ORDERS-007: 点击订单卡片进入详情"""
        orders = OrdersPage(app).navigate()
        if not orders.has_orders():
            pytest.skip("无订单数据")
        result = orders.click_first_order()
        assert result, "无法点击订单卡片"
        app.screenshot("orders_007_order_detail")


@pytest.mark.orders
class TestOrderDetail:
    """订单详情页测试"""

    def test_order_number_displayed(self, app):
        """ORDER-001: 订单编号显示"""
        orders = OrdersPage(app).navigate()
        if orders.has_orders():
            orders.click_first_order()
            detail = OrderDetailPage(app)
            number = detail.get_order_number()
            app.screenshot("order_detail_001_number")
            if number:
                assert len(number) > 0, "订单编号为空"

    def test_order_amount_displayed(self, app):
        """ORDER-002: 订单金额显示"""
        orders = OrdersPage(app).navigate()
        if orders.has_orders():
            orders.click_first_order()
            detail = OrderDetailPage(app)
            amount = detail.get_order_amount()
            app.screenshot("order_detail_002_amount")

    def test_view_voucher(self, app):
        """ORDER-003: 查看协议和凭证"""
        orders = OrdersPage(app).navigate()
        if orders.has_orders():
            orders.click_first_order()
            time.sleep(1)
            detail = OrderDetailPage(app)
            result = detail.click_view_voucher()
            if result:
                assert detail.is_voucher_displayed(), "协议凭证页未显示"
                app.screenshot("order_detail_003_voucher")

    def test_view_invoice(self, app):
        """ORDER-004: 查看发票"""
        orders = OrdersPage(app).navigate()
        if orders.has_orders():
            orders.click_first_order()
            time.sleep(1)
            detail = OrderDetailPage(app)
            result = detail.click_view_invoice()
            if result:
                assert detail.is_invoice_displayed(), "发票页未显示"
                app.screenshot("order_detail_004_invoice")

    def test_download_all(self, app):
        """ORDER-005: 全部下载"""
        orders = OrdersPage(app).navigate()
        if orders.has_orders():
            orders.click_first_order()
            time.sleep(1)
            detail = OrderDetailPage(app)
            # 进入协议凭证页
            detail.click_view_voucher()
            result = detail.click_download_all()
            if result:
                app.screenshot("order_detail_005_download")
