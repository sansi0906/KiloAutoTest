"""
乐云泰App自动化测试 - 商品模块测试用例
"""
import pytest
import time


class TestGoods:
    def test_01_goods_visible(self, app, goods):
        """商品Tab可见"""
        app.go_tab("goods")
        assert goods.is_visible(), "商品Tab不可见"
        app.dm.screenshot("goods_01_visible")

    def test_02_categories(self, app, goods):
        """商品分类"""
        app.go_tab("goods")
        cats = goods.get_categories()
        app.dm.screenshot("goods_02_categories")

    def test_03_switch_category(self, app, goods):
        """切换分类"""
        app.go_tab("goods")
        for cat in goods.CATEGORIES:
            if app.d(text=cat).exists(timeout=1):
                goods.switch_category(cat)
                app.dm.screenshot(f"goods_03_{cat}")

    def test_04_search_goods(self, app, goods):
        """搜索商品"""
        app.go_tab("goods")
        goods.search_goods("消防")
        app.dm.screenshot("goods_04_search")

    def test_05_scroll_goods(self, app, goods):
        """商品列表滑动"""
        app.go_tab("goods")
        goods.scroll_to_load_more()
        app.dm.screenshot("goods_05_scroll")
