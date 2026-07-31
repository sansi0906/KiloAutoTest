"""
津筑网App - 订单页页面对象
"""
import time


class OrdersPage:
    """订单页Page Object"""

    # 订单状态Tab
    STATES = ["全部", "待确认", "进行中", "待评价", "已完成"]

    def __init__(self, app):
        self.app = app
        self.d = app.d

    def navigate(self):
        """导航到订单页"""
        self.app.go_tab("orders")
        return self

    def switch_state(self, state_name):
        """切换订单状态Tab"""
        el = self.d(text=state_name)
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_first_order(self):
        """点击第一个订单卡片"""
        el = self.d(resourceId="com.tjxinyu.fz:id/rl_order_item")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        # 备用：点击坐标
        self.d.click(500, 800)
        time.sleep(2)
        return True

    def get_order_count(self):
        """获取订单列表数量"""
        items = self.d(resourceId="com.tjxinyu.fz:id/rl_order_item")
        return items.count

    def has_orders(self):
        """是否有订单"""
        return self.d(resourceId="com.tjxinyu.fz:id/rl_order_item").exists

    def is_empty(self):
        """订单列表是否为空"""
        el = self.d(text="暂无订单")
        return el.exists


class OrderDetailPage:
    """订单详情页Page Object"""

    def __init__(self, app):
        self.app = app
        self.d = app.d

    def get_order_number(self):
        """获取订单编号"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_order_no")
        if el.exists:
            return el.get_text()
        return ""

    def get_order_amount(self):
        """获取订单金额"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_order_amount")
        if el.exists:
            return el.get_text()
        return ""

    def get_delivery_address(self):
        """获取收货地址"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_address")
        if el.exists:
            return el.get_text()
        return ""

    def click_view_voucher(self):
        """点击查看协议和凭证"""
        el = self.d(text="查看协议和凭证")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_view_invoice(self):
        """点击查看发票"""
        el = self.d(text="查看发票")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_download_all(self):
        """点击全部下载"""
        el = self.d(text="全部下载")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def is_voucher_displayed(self):
        """协议凭证页是否显示"""
        return self.d(text="协议").exists or self.d(text="凭证").exists

    def is_invoice_displayed(self):
        """发票页是否显示"""
        return self.d(text="发票").exists
