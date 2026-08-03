"""
乐云泰App自动化测试 - App操作助手
"""
import time
import os


class AppHelper:
    # 底部Tab坐标 (1080x2400)
    TAB_HOME = (135, 2280)
    TAB_ORDERS = (405, 2280)
    TAB_GOODS = (675, 2280)
    TAB_MINE = (945, 2280)

    def __init__(self, device_manager):
        self.dm = device_manager
        self.d = device_manager.d
        self.package = device_manager.package

    def ensure_app_foreground(self):
        if not self.dm.is_app_foreground():
            self.dm.launch_app()
            self.skip_guide()
            self.dismiss_popups()
        else:
            self.skip_guide()
            self.dismiss_popups()

    def skip_guide(self):
        """跳过引导页"""
        if self.d(text="开始使用").exists(timeout=2):
            for _ in range(3):
                self.d.swipe(0.8, 0.5, 0.1, 0.5, duration=0.3)
                time.sleep(1)
            self.d.click(0.5, 0.803)
            time.sleep(2)

    def go_home_tab(self):
        self.d.click(*self.TAB_HOME)
        time.sleep(1)

    def dismiss_popups(self):
        for keyword in ["忽略本次", "同意", "确定", "允许", "我知道了"]:
            el = self.d(text=keyword)
            if el.exists:
                el.click()
                time.sleep(1.5)
                break

    def screenshot(self, name):
        return self.dm.screenshot(name)

    def go_tab(self, tab_name):
        tabs = {
            "home": self.TAB_HOME,
            "goods": self.TAB_GOODS,
            "orders": self.TAB_ORDERS,
            "mine": self.TAB_MINE,
        }
        coord = tabs.get(tab_name)
        if coord is None:
            raise ValueError(f"未知Tab: {tab_name}")
        self.d.click(*coord)
        time.sleep(1.5)
        self.dismiss_popups()
        time.sleep(0.5)

    def click_text(self, text, timeout=10):
        el = self.d(text=text)
        if el.wait(timeout=timeout):
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_if_exists(self, **kwargs):
        el = self.d(**kwargs)
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def scroll_down(self):
        self.d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
        time.sleep(1)

    def scroll_up(self):
        self.d.swipe(0.5, 0.3, 0.5, 0.7, duration=0.5)
        time.sleep(1)

    def back(self):
        self.d.press("back")
        time.sleep(1.5)

    def is_text_present(self, text):
        return self.d(text=text).exists
