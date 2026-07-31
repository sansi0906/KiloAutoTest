"""
津筑网App - 我的页面页面对象
"""
import time


class MinePage:
    """我的页面Page Object"""

    def __init__(self, app):
        self.app = app
        self.d = app.d

    def navigate(self):
        """导航到我的页面"""
        self.app.go_tab("mine")
        return self

    def get_user_name(self):
        """获取用户昵称"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_user_name")
        if el.exists:
            return el.get_text()
        return ""

    def get_user_phone(self):
        """获取用户手机号"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_user_phone")
        if el.exists:
            return el.get_text()
        return ""

    def click_avatar(self):
        """点击用户头像"""
        el = self.d(resourceId="com.tjxinyu.fz:id/iv_avatar")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_member_management(self):
        """点击成员管理"""
        el = self.d(text="成员管理")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        # 备用：通过resourceId
        el = self.d(resourceId="com.tjxinyu.fz:id/ll_member")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_address(self):
        """点击收货地址"""
        el = self.d(text="收货地址")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_company_qualification(self):
        """点击公司资质"""
        el = self.d(text="公司资质")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_feedback(self):
        """点击意见反馈"""
        el = self.d(text="意见反馈")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_settings(self):
        """点击系统设置"""
        el = self.d(text="系统设置")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_about_us(self):
        """点击关于我们"""
        el = self.d(text="关于我们")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def get_customer_service_phone(self):
        """获取客服电话"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_service_phone")
        if el.exists:
            return el.get_text()
        return ""

    def click_customer_service(self):
        """点击客服电话"""
        el = self.d(resourceId="com.tjxinyu.fz:id/tv_service_phone")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False
