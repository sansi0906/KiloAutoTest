"""
乐云泰App自动化测试 - 订单模块测试用例
"""
import pytest
import time


class TestOrders:
    def test_01_orders_visible(self, app, orders):
        """订单Tab可见"""
        app.go_tab("orders")
        assert orders.is_visible(), "订单Tab不可见"
        app.dm.screenshot("orders_01_visible")

    def test_02_order_tabs(self, app, orders):
        """订单状态Tab"""
        app.go_tab("orders")
        tabs = orders.get_order_tabs()
        app.dm.screenshot("orders_02_tabs")

    def test_03_switch_tab(self, app, orders):
        """切换订单Tab"""
        app.go_tab("orders")
        for tab in orders.ORDER_TABS:
            if app.d(text=tab).exists(timeout=1):
                orders.switch_order_tab(tab)
                app.dm.screenshot(f"orders_03_{tab}")

    def test_04_scroll_orders(self, app, orders):
        """订单列表滑动"""
        app.go_tab("orders")
        orders.get_order_list()
        app.scroll_down()
        app.dm.screenshot("orders_04_scroll")
