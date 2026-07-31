"""
津筑网App自动化测试 - App操作助手
封装页面导航、弹窗处理、截图等通用操作
"""
import time
import os


class AppHelper:
    """App通用操作助手"""

    # 底部Tab坐标（基于小米13 1080x2400）
    TAB_HOME = (135, 2336)
    TAB_GOODS = (405, 2336)
    TAB_ORDERS = (675, 2336)
    TAB_MINE = (945, 2336)

    def __init__(self, device_manager):
        self.dm = device_manager
        self.d = device_manager.d
        self.package = device_manager.package

    # ==================== App状态管理 ====================

    def ensure_app_foreground(self):
        """确保App在前台，否则启动"""
        if not self.dm.is_app_foreground():
            self.dm.launch_app()
            self.dismiss_popups()
        else:
            self.dismiss_popups()

    def go_home_tab(self):
        """回到首页Tab"""
        self.d.click(*self.TAB_HOME)
        time.sleep(1)

    # ==================== 弹窗处理 ====================

    def dismiss_popups(self):
        """处理各种弹窗（版本更新、隐私政策等）"""
        handled = False
        for keyword in ["忽略本次", "同意", "确定", "允许", "我知道了"]:
            el = self.d(text=keyword)
            if el.exists:
                el.click()
                print(f"  💬 处理弹窗: {keyword}")
                time.sleep(1.5)
                handled = True
                break
        return handled

    # ==================== 截图 ====================

    def screenshot(self, name):
        """截图保存"""
        return self.dm.screenshot(name)

    # ==================== 页面导航 ====================

    def go_tab(self, tab_name):
        """切换底部Tab
        Args:
            tab_name: home / goods / orders / mine
        """
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
        time.sleep(2)
        self.dismiss_popups()

    # ==================== 通用操作 ====================

    def click_text(self, text, timeout=10):
        """通过文字点击元素"""
        el = self.d(text=text)
        if el.wait(timeout=timeout):
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_if_exists(self, **kwargs):
        """如果元素存在则点击"""
        el = self.d(**kwargs)
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def find_element(self, **kwargs):
        """查找元素，返回uiautomator2元素对象"""
        return self.d(**kwargs)

    def wait_for_text(self, text, timeout=10):
        """等待文字出现"""
        return self.d(text=text).wait(timeout=timeout)

    def scroll_down(self):
        """向下滑动"""
        self.d.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
        time.sleep(1)

    def scroll_up(self):
        """向上滑动"""
        self.d.swipe(0.5, 0.3, 0.5, 0.7, duration=0.5)
        time.sleep(1)

    def back(self):
        """返回"""
        self.d.press("back")
        time.sleep(1.5)

    def get_current_activity(self):
        """获取当前Activity"""
        info = self.d.app_current()
        return info.get("activity", "")

    def is_text_present(self, text):
        """检查页面是否包含指定文字"""
        return self.d(text=text).exists
