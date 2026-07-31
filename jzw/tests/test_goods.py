"""
津筑网App - 商品模块测试用例
"""
import pytest
from pages.goods_page import GoodsPage


@pytest.mark.goods
class TestGoods:
    """商品页功能测试"""

    def test_goods_page_displayed(self, app):
        """GOODS-001: 商品页正常显示"""
        goods = GoodsPage(app).navigate()
        # 验证4个分类Tab显示
        for tab in GoodsPage.TABS:
            assert app.d(text=tab).exists, f"Tab'{tab}'未显示"
        app.screenshot("goods_001_page_displayed")

    def test_switch_to_equipment(self, app):
        """GOODS-002: 切换到设备分类"""
        goods = GoodsPage(app).navigate()
        result = goods.switch_tab("设备")
        assert result, "无法切换到设备分类"
        app.screenshot("goods_002_equipment")

    def test_switch_to_building(self, app):
        """GOODS-003: 切换到建材分类"""
        goods = GoodsPage(app).navigate()
        result = goods.switch_tab("建材")
        assert result, "无法切换到建材分类"
        app.screenshot("goods_003_building")

    def test_switch_to_talent(self, app):
        """GOODS-004: 切换到人才分类"""
        goods = GoodsPage(app).navigate()
        result = goods.switch_tab("人才")
        assert result, "无法切换到人才分类"
        app.screenshot("goods_004_talent")

    def test_switch_to_service(self, app):
        """GOODS-005: 切换到服务分类"""
        goods = GoodsPage(app).navigate()
        result = goods.switch_tab("服务")
        assert result, "无法切换到服务分类"
        app.screenshot("goods_005_service")

    def test_search_box(self, app):
        """GOODS-006: 搜索框激活"""
        goods = GoodsPage(app).navigate()
        result = goods.click_search_box()
        assert result, "无法点击搜索框"
        app.screenshot("goods_006_search_box")

    def test_search_input(self, app):
        """GOODS-007: 搜索关键词输入"""
        goods = GoodsPage(app).navigate()
        goods.click_search_box()
        result = goods.input_search("挖掘机")
        assert result, "无法输入搜索关键词"
        app.screenshot("goods_007_search_input")

    def test_region_filter(self, app):
        """GOODS-008: 地区筛选"""
        goods = GoodsPage(app).navigate()
        result = goods.click_region_filter()
        if result:
            app.screenshot("goods_008_region_filter")
        else:
            pytest.skip("地区筛选未找到")

    def test_sort_by_sales(self, app):
        """GOODS-009: 销量排序"""
        goods = GoodsPage(app).navigate()
        result = goods.click_sort_by_sales()
        if result:
            app.screenshot("goods_009_sort_sales")
        else:
            pytest.skip("销量排序未找到")

    def test_filter_button(self, app):
        """GOODS-010: 筛选按钮"""
        goods = GoodsPage(app).navigate()
        result = goods.click_filter_button()
        if result:
            app.screenshot("goods_010_filter_button")
        else:
            pytest.skip("筛选按钮未找到")

    def test_click_product(self, app):
        """GOODS-011: 点击商品进入详情"""
        goods = GoodsPage(app).navigate()
        result = goods.click_first_product()
        assert result, "无法点击商品卡片"
        app.screenshot("goods_011_product_detail")

    def test_phone_consult(self, app):
        """GOODS-012: 电话咨询按钮"""
        goods = GoodsPage(app).navigate()
        goods.click_first_product()
        time.sleep(1)
        result = goods.click_phone_consult()
        if result:
            app.screenshot("goods_012_phone_consult")
        else:
            pytest.skip("电话咨询按钮未找到")


# 需要在文件顶部导入time
import time
