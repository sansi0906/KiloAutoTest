"""重点项目模块测试"""
import pytest

class TestKeyProjects:
    """重点项目测试类"""

    def test_project_card_display(self, page):
        """P01-001: 项目卡片展示"""
        project_cards = page.locator("div[class*='card'], div[class*='project']")
        assert project_cards.count() > 0, "未找到项目卡片"

    def test_project_click(self, page):
        """P02-001: 项目点击"""
        from conftest import click_and_wait_for_new_page
        
        project_title = page.locator("div[class*='card'] h3, div[class*='card'] h4, div[class*='card'] [class*='title'], div[class*='card'] a").first
        if project_title.is_visible():
            result_page = click_and_wait_for_new_page(page, project_title)
            assert "详情" in result_page.content()

    def test_project_detail_info(self, page):
        """P02-002: 详情页面内容"""
        from conftest import click_and_wait_for_new_page
        
        project_card = page.locator("div[class*='card']").first
        if project_card.is_visible():
            result_page = click_and_wait_for_new_page(page, project_card)
            assert "keyProject/detail" in result_page.url, f"URL中未包含keyProject/detail，当前URL: {result_page.url}"

    def test_view_all_projects(self, page):
        """P03-001: 查看全部链接"""
        view_all_btn = page.locator("text=查看全部").first
        view_all_btn.click()
        page.wait_for_load_state("networkidle")
        assert "project" in page.url.lower() or "demand" in page.url.lower()
