"""
津筑网App - 系统设置页页面对象
"""
import time


class SettingsPage:
    """系统设置页Page Object"""

    def __init__(self, app):
        self.app = app
        self.d = app.d

    def navigate(self):
        """从我的页面进入系统设置"""
        from pages.mine_page import MinePage
        MinePage(self.app).navigate()
        el = self.d(text="系统设置")
        if el.wait(timeout=5):
            el.click()
            time.sleep(2)
            return self
        return None

    def click_logout(self):
        """点击退出登录"""
        el = self.d(text="退出登录")
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def confirm_logout(self):
        """确认退出登录"""
        el = self.d(text="确定")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def cancel_logout(self):
        """取消退出登录"""
        el = self.d(text="取消")
        if el.exists:
            el.click()
            time.sleep(1)
            return True
        return False

    def is_logout_dialog_displayed(self):
        """检查退出登录弹窗是否显示"""
        return self.d(text="您确定要退出登录吗").exists or \
               (self.d(text="确定").exists and self.d(text="取消").exists)

    def click_cancel_account(self):
        """点击注销账户"""
        el = self.d(text="注销账户")
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def is_cancel_account_dialog_displayed(self):
        """检查注销账户弹窗是否显示"""
        return self.d(textContains="注销").exists and \
               (self.d(text="确定").exists or self.d(text="取消").exists)

    def cancel_cancel_account(self):
        """取消注销账户"""
        el = self.d(text="取消")
        if el.exists:
            el.click()
            time.sleep(1)
            return True
        return False
