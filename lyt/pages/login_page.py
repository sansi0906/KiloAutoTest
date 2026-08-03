"""
乐云泰App - 登录页面对象
"""
import time


class LoginPage:
    def __init__(self, device):
        self.d = device

    COORDS = {
        "phone_input": (540, 1000),
        "pwd_input": (540, 1180),
        "agreement": (230, 1330),
        "login_btn": (540, 1310),
        "guide_button": (540, 1927),
        "password_tab": (540, 1700),
    }

    def skip_guide_if_present(self):
        if self.d(text="开始使用").exists(timeout=2):
            for _ in range(3):
                self.d.swipe(0.8, 0.5, 0.1, 0.5, duration=0.3)
                time.sleep(1)
            self.d.click(0.5, 0.803)
            time.sleep(2)
            return True
        return False

    def dismiss_all_dialogs(self):
        dialogs = [
            "同意", "关闭", "允许", "确定", "忽略本次", "我知道了",
            "拒绝并退出", "取消", "始终允许", "仅本次允许"
        ]
        for text in dialogs:
            if self.d(text=text).exists(timeout=0.3):
                self.d(text=text).click()
                time.sleep(0.3)

    def dismiss_miui_clipboard(self):
        """处理小米剪贴板提醒"""
        if self.d(text="关闭").exists(timeout=0.5):
            self.d(text="关闭").click()
            time.sleep(0.5)
            return True
        return False

    def switch_to_password_login(self):
        if self.d(text="密码登录").exists(timeout=2):
            self.d(text="密码登录").click()
            time.sleep(1)
            return True
        if self.d(text="请输入密码").exists(timeout=1):
            return True
        return False

    def _get_phone_field(self):
        """获取手机号输入框"""
        return self.d(className="android.widget.EditText")[0]

    def _get_pwd_field(self):
        """获取密码输入框"""
        return self.d(className="android.widget.EditText")[1]

    def input_phone(self, phone):
        try:
            field = self._get_phone_field()
            field.click()
            field.clear_text()
            field.set_text(phone)
            return True
        except Exception:
            x, y = self.COORDS["phone_input"]
            self.d.click(x, y)
            time.sleep(0.3)
            self.d.clear_text()
            self.d.send_keys(phone)
            return True

    def input_password(self, password):
        try:
            field = self._get_pwd_field()
            field.click()
            field.clear_text()
            field.set_text(password)
            return True
        except Exception:
            x, y = self.COORDS["pwd_input"]
            self.d.click(x, y)
            time.sleep(0.3)
            self.d.clear_text()
            for ch in password:
                self.d.send_keys(ch)
                time.sleep(0.03)
            return True

    def check_agreement(self):
        try:
            cb = self.d(className="android.widget.CheckBox")
            if cb.exists(timeout=1):
                if not cb.info.get("checked", False):
                    cb.click()
                    return True
        except Exception:
            pass
        x, y = self.COORDS["agreement"]
        self.d.click(x, y)
        time.sleep(0.3)
        return True

    def click_login(self):
        if self.d(text="登录").exists(timeout=2):
            self.d(text="登录").click()
            return True
        x, y = self.COORDS["login_btn"]
        self.d.click(x, y)
        return True

    def login_with_password(self, phone, password):
        self.skip_guide_if_present()
        self.dismiss_all_dialogs()
        self.switch_to_password_login()
        self.dismiss_miui_clipboard()
        self.input_phone(phone)
        self.input_password(password)
        self.dismiss_miui_clipboard()
        self.check_agreement()
        self.dismiss_all_dialogs()
        self.click_login()
        time.sleep(5)
        self.dismiss_all_dialogs()

    def is_login_successful(self):
        return any(
            self.d(text=tab).exists(timeout=1)
            for tab in ["首页", "订单", "商品", "我的"]
        )

    def is_on_login_page(self):
        keywords = ["请输入手机号", "一键登录", "验证码登录", "请输入密码"]
        return any(self.d(text=kw).exists(timeout=1) for kw in keywords)
