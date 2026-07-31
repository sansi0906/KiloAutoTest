"""
津筑网App - 登录页页面对象
"""
import time


class LoginPage:
    """登录页Page Object"""

    def __init__(self, app):
        self.app = app
        self.d = app.d

    # ==================== 验证码登录 ====================

    def input_phone(self, phone):
        """输入手机号"""
        el = self.d(resourceId="com.tjxinyu.fz:id/et_phone")
        if el.wait(timeout=5):
            el.clear_text()
            el.send_keys(phone)
            time.sleep(0.5)
            return True
        return False

    def click_get_code(self):
        """点击获取验证码"""
        el = self.d(resourceId="com.tjxinyu.fz:id/btn_get_code")
        if el.exists:
            el.click()
            time.sleep(1)
            return True
        return False

    def input_code(self, code):
        """输入验证码"""
        el = self.d(resourceId="com.tjxinyu.fz:id/et_code")
        if el.wait(timeout=5):
            el.send_keys(code)
            time.sleep(0.5)
            return True
        return False

    def click_login(self):
        """点击登录按钮"""
        el = self.d(resourceId="com.tjxinyu.fz:id/btn_login")
        if el.exists:
            el.click()
            time.sleep(3)
            return True
        el = self.d(text="登录")
        if el.exists:
            el.click()
            time.sleep(3)
            return True
        return False

    def login_with_code(self, phone, code):
        """验证码登录完整流程"""
        self.input_phone(phone)
        self.click_get_code()
        self.input_code(code)
        return self.click_login()

    # ==================== 登录状态检查 ====================

    def is_login_success(self):
        """检查是否登录成功（是否出现首页特征）"""
        # 登录成功后会进入首页
        time.sleep(2)
        if self.d(text="设备").exists and self.d(text="建材").exists:
            return True
        if self.d(resourceId="com.tjxinyu.fz:id/tv_welcome").exists:
            return True
        return False

    def is_login_page(self):
        """检查是否在登录页"""
        return self.d(resourceId="com.tjxinyu.fz:id/et_phone").exists or \
               self.d(text="登录").exists
