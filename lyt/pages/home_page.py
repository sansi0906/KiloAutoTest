"""
乐云泰App - 首页页面对象
"""
import time


class HomePage:
    TAB_NAME = "首页"

    def __init__(self, device):
        self.d = device

    def is_visible(self):
        return self.d(text=self.TAB_NAME).exists(timeout=2)

    def get_home_elements(self):
        """获取首页元素"""
        xml = self.d.dump_hierarchy()
        import re
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]

    def scroll_to_top(self):
        self.d.swipe(0.5, 0.3, 0.5, 0.8, duration=0.5)
        time.sleep(1)

    def scroll_to_bottom(self):
        self.d.swipe(0.5, 0.7, 0.5, 0.2, duration=0.5)
        time.sleep(1)

    def click_banner(self, index=0):
        """点击轮播图"""
        banners = self.d(resourceId="com.grl.leyuntai:id/vp_banner")
        if banners.exists:
            banners.click()
            time.sleep(2)
            return True
        return False

    def search(self, keyword):
        """搜索"""
        search = self.d(text="搜索")
        if search.exists(timeout=3):
            search.click()
            time.sleep(1)
            self.d.send_keys(keyword)
            self.d.press("enter")
            time.sleep(2)
            return True
        return False

    def click_news(self, title):
        """点击资讯"""
        el = self.d(text=title)
        if el.exists(timeout=3):
            el.click()
            time.sleep(2)
            return True
        return False
