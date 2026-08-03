"""
乐云泰App - 我的页面对象
"""
import time


class MinePage:
    TAB_NAME = "我的"

    def __init__(self, device):
        self.d = device

    def is_visible(self):
        return self.d(text=self.TAB_NAME).exists(timeout=2)

    def get_user_info(self):
        """获取用户信息"""
        xml = self.d.dump_hierarchy()
        import re
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]

    def click_menu(self, menu_name):
        """点击菜单项"""
        el = self.d(text=menu_name)
        if el.exists(timeout=3):
            el.click()
            time.sleep(2)
            return True
        return False

    def check_login_status(self):
        """检查登录状态"""
        indicators = ["退出登录", "注销账户", "账号管理"]
        for ind in indicators:
            if self.d(text=ind).exists(timeout=1):
                return True
        return False

    def logout(self):
        """退出登录"""
        if self.d(text="退出登录").exists(timeout=2):
            self.d(text="退出登录").click()
            time.sleep(1)
            if self.d(text="确定").exists(timeout=1):
                self.d(text="确定").click()
                time.sleep(2)
            return True
        return False
