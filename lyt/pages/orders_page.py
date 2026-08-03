"""
乐云泰App - 订单页面对象
"""
import time


class OrdersPage:
    TAB_NAME = "订单"

    ORDER_TABS = ["全部", "待付款", "待发货", "待收货", "已完成"]

    def __init__(self, device):
        self.d = device

    def is_visible(self):
        return self.d(text=self.TAB_NAME).exists(timeout=2)

    def get_order_tabs(self):
        return [t for t in self.ORDER_TABS if self.d(text=t).exists(timeout=1)]

    def switch_order_tab(self, tab_name):
        if self.d(text=tab_name).exists(timeout=2):
            self.d(text=tab_name).click()
            time.sleep(1.5)
            return True
        return False

    def get_order_list(self):
        """获取订单列表"""
        xml = self.d.dump_hierarchy()
        import re
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]

    def click_order_detail(self, order_text):
        el = self.d(text=order_text)
        if el.exists(timeout=3):
            el.click()
            time.sleep(2)
            return True
        return False

    def swipe_left_on_order(self):
        """订单左滑"""
        self.d.swipe(0.8, 0.5, 0.2, 0.5, duration=0.5)
        time.sleep(1)

    def click_action(self, action):
        """点击订单操作按钮"""
        if self.d(text=action).exists(timeout=2):
            self.d(text=action).click()
            time.sleep(2)
            return True
        return False
