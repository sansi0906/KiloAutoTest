"""
津筑网App - 首页页面对象
"""
import time


class HomePage:
    """首页Page Object"""

    # 分类入口文字
    CATEGORIES = ["设备", "建材", "人才", "服务"]

    def __init__(self, app):
        self.app = app
        self.d = app.d

    def navigate(self):
        """导航到首页"""
        self.app.go_tab("home")
        return self

    def get_welcome_text(self):
        """获取欢迎语文本"""
        # 欢迎语区域通常在顶部
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_welcome")
        if el.exists:
            return el.get_text()
        # 备用：通过包含"欢迎"的文本查找
        for node in self.d.xpath("//android.widget.TextView[contains(@text, '欢迎')]").all():
            return node.text
        return ""

    def click_category(self, name):
        """点击分类入口（设备/建材/人才/服务）"""
        el = self.d(text=name)
        if el.exists:
            el.click()
            time.sleep(2)
            self.app.dismiss_popups()
            return True
        return False

    def click_transaction_stat(self):
        """点击交易统计数字"""
        # 交易统计区域
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_transaction_count")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        # 备用：点击坐标
        self.d.click(295, 1256)
        time.sleep(2)
        return True

    def click_order_status(self, status_name):
        """点击订单状态数字（待确认/进行中/待评价/已完成）"""
        el = self.d(text=status_name)
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_all_orders(self):
        """点击全部订单"""
        el = self.d(text="全部订单")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_message_card(self):
        """点击消息卡片"""
        el = self.d(text="点击查看")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        el = self.d(resourceId="com.tjxinyu.fz:id/ll_message")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def is_category_displayed(self, name):
        """检查分类是否显示"""
        return self.d(text=name).exists
