"""
津筑网App - 商品页页面对象
"""
import time


class GoodsPage:
    """商品页Page Object"""

    # 顶部分类
    TABS = ["设备", "建材", "人才", "服务"]

    def __init__(self, app):
        self.app = app
        self.d = app.d

    def navigate(self):
        """导航到商品页"""
        self.app.go_tab("goods")
        return self

    def switch_tab(self, tab_name):
        """切换顶部分类Tab"""
        el = self.d(text=tab_name)
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_search_box(self):
        """点击搜索框"""
        el = self.d(resourceId="com.tjxinyu.fz:id/et_search")
        if el.exists:
            el.click()
            time.sleep(1)
            return True
        el = self.d(className="android.widget.EditText")
        if el.exists:
            el.click()
            time.sleep(1)
            return True
        return False

    def input_search(self, keyword):
        """输入搜索关键词"""
        el = self.d(resourceId="com.tjxinyu.fz:id/et_search")
        if not el.exists:
            self.click_search_box()
        self.d.send_keys(keyword)
        time.sleep(0.5)
        return True

    def click_search_button(self):
        """点击搜索按钮"""
        el = self.d(resourceId="com.tjxinyu.fz:id/btn_search")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        el = self.d(text="搜索")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def click_region_filter(self):
        """点击地区筛选"""
        el = self.d(text="地区")
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_sort_by_sales(self):
        """点击销量排序"""
        el = self.d(text="销量")
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_filter_button(self):
        """点击筛选按钮"""
        el = self.d(text="筛选")
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        el = self.d(resourceId="com.tjxinyu.fz:id/iv_filter")
        if el.exists:
            el.click()
            time.sleep(1.5)
            return True
        return False

    def click_first_product(self):
        """点击第一个商品卡片"""
        # 尝试通过resourceId定位
        el = self.d(resourceId="com.tjxinyu.fz:id/rl_product_item")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        # 备用：点击坐标
        self.d.click(300, 800)
        time.sleep(2)
        return True

    def click_phone_consult(self):
        """点击电话咨询"""
        el = self.d(text="电话咨询")
        if el.exists:
            el.click()
            time.sleep(2)
            return True
        return False

    def get_product_list_count(self):
        """获取商品列表数量"""
        items = self.d(resourceId="com.tjxinyu.fz:id/rl_product_item")
        return items.count

    def is_product_displayed(self):
        """检查是否有商品显示"""
        return self.d(resourceId="com.tjxinyu.fz:id/rl_product_item").exists
