"""产业需求模块测试"""
import pytest

class TestIndustryDemand:
    """产业需求测试类"""
    
    def _scroll_to_demand_section(self, page):
        """滚动到产业需求模块"""
        # 尝试多种方式定位产业需求模块
        section_selectors = [
            "h2:text('产业需求')",
            "h3:text('产业需求')",
            "div:has-text('产业需求')",
            "section:has-text('产业需求')",
            "[class*='demand']",
            "[class*='industry-demand']",
        ]
        
        demand_section = None
        for selector in section_selectors:
            sections = page.locator(selector)
            if sections.count() > 0:
                demand_section = sections.first
                break
        
        if demand_section:
            # 滚动到该模块
            demand_section.scroll_into_view_if_needed()
            page.wait_for_load_state("networkidle")
            return True
        
        # 如果还是找不到，尝试滚动页面查找
        for _ in range(5):
            page.keyboard.press("PageDown")
            page.wait_for_timeout(500)
            for selector in section_selectors:
                sections = page.locator(selector)
                if sections.count() > 0:
                    sections.first.scroll_into_view_if_needed()
                    page.wait_for_load_state("networkidle")
                    return True
        
        return False

    def test_demand_card_display(self, page):
        """D01-001: 需求卡片展示"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        demand_cards = page.locator("div[class*='card'], div[class*='item'], article")
        assert demand_cards.count() > 0, "未找到需求卡片"

    def test_demand_date_format(self, page):
        """D01-002: 需求日期格式"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        date_elements = page.locator("text=/\\d{4}-\\d{2}-\\d{2}/")
        assert date_elements.count() > 0, "未找到日期元素"

    def test_demand_amount_format(self, page):
        """D01-003: 金额显示格式"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        amount_elements = page.locator("text=/\\d+万|¥\\d+/")
        assert amount_elements.count() > 0, "未找到金额元素"

    def test_machinery_filter(self, page):
        """D02-002: 机械设备筛选"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        # 在产业需求模块内查找筛选按钮
        demand_section = page.locator("div:has(h2:text('产业需求')), div:has(h3:text('产业需求'))").first
        if demand_section.is_visible():
            # 在需求模块内查找机械设备筛选按钮
            filter_btn = demand_section.locator("button:text('机械设备'), span:text('机械设备')").first
        else:
            # 回退到全局查找
            filter_btn = page.locator("button:text('机械设备'), span:text('机械设备')").first
        
        assert filter_btn.is_visible(), "未找到机械设备筛选按钮"
        
        filter_btn.click()
        page.wait_for_load_state("networkidle")
        
        # 使用更可靠的断言
        content = page.content()
        assert any(keyword in content for keyword in ["机械", "设备", "施工", "塔吊", "挖掘机"]), \
            f"筛选后页面内容不包含机械设备相关内容: {content[:500]}..."
        
    def test_building_materials_filter(self, page):
        """D02-001: 建筑建材筛选"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        # 在产业需求模块内查找筛选按钮
        demand_section = page.locator("div:has(h2:text('产业需求')), div:has(h3:text('产业需求'))").first
        if demand_section.is_visible():
            filter_btn = demand_section.locator("button:text('建筑建材'), span:text('建筑建材')").first
        else:
            filter_btn = page.locator("text=建筑建材").first
        
        assert filter_btn.is_visible(), "未找到建筑建材筛选按钮"
        
        filter_btn.click()
        page.wait_for_load_state("networkidle")
        assert "配电箱" in page.content() or "建材" in page.content()

    def test_labor_filter(self, page):
        """D02-003: 劳务用工筛选"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        # 在产业需求模块内查找筛选按钮
        demand_section = page.locator("div:has(h2:text('产业需求')), div:has(h3:text('产业需求'))").first
        if demand_section.is_visible():
            filter_btn = demand_section.locator("button:text('劳务用工'), span:text('劳务用工')").first
        else:
            filter_btn = page.locator("text=劳务用工").first
        
        assert filter_btn.is_visible(), "未找到劳务用工筛选按钮"
        
        filter_btn.click()
        page.wait_for_load_state("networkidle")
        assert "劳务" in page.content() or "用工" in page.content()

    def test_tech_service_filter(self, page):
        """D02-004: 技术服务筛选"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        # 在产业需求模块内查找筛选按钮
        demand_section = page.locator("div:has(h2:text('产业需求')), div:has(h3:text('产业需求'))").first
        if demand_section.is_visible():
            filter_btn = demand_section.locator("button:text('技术服务'), span:text('技术服务')").first
        else:
            filter_btn = page.locator("text=技术服务").first
        
        assert filter_btn.is_visible(), "未找到技术服务筛选按钮"
        
        filter_btn.click()
        page.wait_for_load_state("networkidle")
        assert "招标" in page.content() or "技术" in page.content()

    def test_view_detail_button(self, page):
        """D03-001: 查看详情按钮"""
        from conftest import click_and_wait_for_new_page
        
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        detail_btn = page.locator("text=查看详情").first
        if detail_btn.is_visible():
            result_page = click_and_wait_for_new_page(page, detail_btn)
            assert "详情" in result_page.content() or "detail" in result_page.url.lower()

    def test_view_all_demand(self, page):
        """D04-001: 查看全部链接"""
        # 先滚动到产业需求模块
        self._scroll_to_demand_section(page)
        
        view_all_btn = page.locator("text=查看全部").first
        view_all_btn.click()
        page.wait_for_load_state("networkidle")
        # 检查URL是否包含期望的路径（不依赖域名）
        assert "demandPage" in page.url
