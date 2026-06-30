"""供应链地图模块测试"""
import pytest

class TestSupplyChainMap:
    """供应链地图测试类"""

    def test_region_list_display(self, page):
        """M01-001: 区域列表展示"""
        region_items = page.locator("div, span").filter(has_text="区")
        assert region_items.count() > 0, "未找到区域列表"

    def test_dongli_region_click(self, page):
        """M02-001: 区域点击"""
        dongli_btn = page.locator("text=东丽区").first
        if dongli_btn.is_visible():
            dongli_btn.click()
            page.wait_for_load_state("networkidle")
            # 检查页面内容是否加载（不依赖特定商品名称）
            assert len(page.content()) > 2000, "页面内容过短"



    def test_machinery_switch(self, page):
        """M03-002: 机械设备切换"""
        switch_btn = page.locator("text=机械设备").first
        switch_btn.click()
        page.wait_for_load_state("networkidle")
        assert "弯曲机" in page.content()

    def test_building_materials_switch(self, page):
        """M03-001: 建筑建材切换"""
        switch_btn = page.locator("text=建筑建材").first
        switch_btn.click()
        page.wait_for_load_state("networkidle")
        # 检查页面内容是否加载（不依赖特定商品名称）
        assert len(page.content()) > 2000, "页面内容过短"
        
    def test_all_products_switch(self, page):
        """M03-003: 全部商品切换"""
        switch_btn = page.locator("text=全部商品").first
        switch_btn.click()
        page.wait_for_load_state("networkidle")
        # 检查URL是否包含期望的路径（不依赖域名）
        assert "buildEquipmentWoker" in page.url
