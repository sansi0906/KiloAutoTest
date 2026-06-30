"""供应大厅模块测试"""
import pytest

class TestSupplyHall:
    """供应大厅测试类"""

    def test_machinery_equipment_category(self, page):
        """S01-002: 机械设备分类"""
        from conftest import click_and_wait_for_new_page
        
        btn = page.locator("text=机械设备").first
        result_page = click_and_wait_for_new_page(page, btn)
        # 检查页面内容或URL是否包含机械设备相关信息
        assert "机械" in result_page.content() or "设备" in result_page.content() or "machinery" in result_page.url.lower()

    def test_building_materials_category(self, page):
        """S01-001: 建筑建材分类"""
        btn = page.locator("text=建筑建材").first
        btn.click()
        page.wait_for_load_state("networkidle")
        assert "建材" in page.title() or "建筑" in page.title()

    def test_labor_service_category(self, page):
        """S01-003: 劳务用工分类"""
        from conftest import click_and_wait_for_new_page
        
        btn = page.locator("text=劳务用工").first
        result_page = click_and_wait_for_new_page(page, btn)
        # 检查页面内容或URL是否包含劳务相关信息
        assert "劳务" in result_page.content() or "用工" in result_page.content() or "labor" in result_page.url.lower()

    def test_wenshi_subitem(self, page):
        """S02-001: 文施子项"""
        wenshi_btn = page.locator("text=文施").first
        if wenshi_btn.is_visible():
            wenshi_btn.click()
            page.wait_for_load_state("networkidle")
            assert "消防" in page.content() or "文施" in page.title()

    def test_concrete_category(self, page):
        """S03-001: 混凝土品类"""
        # 使用逗号分隔多个选择器实现"或"逻辑
        concrete_btn = page.locator("text=预拌混凝土, text=混凝土").first
        if concrete_btn.is_visible():
            concrete_btn.click()
            page.wait_for_load_state("networkidle")
            expected_url = "https://www.tjjzcy.com/buildEquipmentWoker"
            assert expected_url in page.url
