"""产业新闻模块测试"""
import pytest

class TestIndustryNews:
    """产业新闻测试类"""

    def test_news_card_display(self, page):
        """N01-001: 新闻卡片展示"""
        news_cards = page.locator("div[class*='card'], article, section")
        assert news_cards.count() > 0, "未找到新闻卡片"

    def test_news_images_load(self, page):
        """N01-002: 新闻图片加载"""
        news_images = page.locator("img")
        if news_images.count() > 0:
            img = news_images.first
            assert img.evaluate("img => img.complete && img.naturalHeight > 0")

    def test_news_click(self, page):
        """N02-001: 新闻点击"""
        from conftest import click_and_wait_for_new_page
        
        news_title = page.locator("div[class*='card'] h3, div[class*='card'] h4, div[class*='card'] [class*='title'], div[class*='card'] a").first
        if news_title.is_visible():
            result_page = click_and_wait_for_new_page(page, news_title)
            assert "新闻" in result_page.content() or "详情" in result_page.content()

    def test_news_detail_content(self, page):
        """N02-002: 详情页面内容"""
        from conftest import click_and_wait_for_new_page
        
        news_title = page.locator("div[class*='card'] h3, div[class*='card'] h4, div[class*='card'] [class*='title'], div[class*='card'] a").first
        if news_title.is_visible():
            result_page = click_and_wait_for_new_page(page, news_title)
            assert len(result_page.content()) > 1000, "新闻内容过短"
