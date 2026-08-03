"""
乐云泰App - 商品页面对象
"""
import time


class GoodsPage:
    TAB_NAME = "商品"

    CATEGORIES = ["全部", "热卖", "新品", "促销"]

    def __init__(self, device):
        self.d = device

    def is_visible(self):
        return self.d(text=self.TAB_NAME).exists(timeout=2)

    def get_categories(self):
        return [c for c in self.CATEGORIES if self.d(text=c).exists(timeout=1)]

    def switch_category(self, cat_name):
        if self.d(text=cat_name).exists(timeout=2):
            self.d(text=cat_name).click()
            time.sleep(1.5)
            return True
        return False

    def search_goods(self, keyword):
        search = self.d(className="android.widget.EditText")
        if search.exists(timeout=3):
            search.click()
            search.clear_text()
            search.set_text(keyword)
            self.d.press("enter")
            time.sleep(2)
            return True
        return False

    def click_goods(self, name):
        el = self.d(text=name)
        if el.exists(timeout=3):
            el.click()
            time.sleep(2)
            return True
        return False

    def get_goods_list(self):
        xml = self.d.dump_hierarchy()
        import re
        texts = re.findall(r'text="([^"]*)"', xml)
        return [t for t in texts if t.strip()]

    def scroll_to_load_more(self):
        self.d.swipe(0.5, 0.7, 0.5, 0.2, duration=1)
        time.sleep(1.5)
