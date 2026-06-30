"""交互与性能测试"""
import pytest

class TestInteractionPerformance:
    """交互与性能测试类"""

    def test_button_hover_effect(self, page):
        """IN01-001: hover效果"""
        buttons = page.locator("button, a[role='button']")
        if buttons.count() > 0:
            btn = buttons.first
            btn.hover()
            initial_color = btn.evaluate("btn => window.getComputedStyle(btn).backgroundColor")
            assert initial_color is not None

    def test_button_click_feedback(self, page):
        """IN01-002: 点击反馈"""
        buttons = page.locator("button:not(:disabled)")
        if buttons.count() > 0:
            btn = buttons.first
            btn.click()
            page.wait_for_load_state("networkidle")

    def test_internal_links(self, page):
        """IN02-001: 内部链接"""
        internal_links = page.locator("a[href^='/'], a[href^='https://www.tjjzcy.com']")
        for i in range(min(internal_links.count(), 5)):
            link = internal_links.nth(i)
            if link.is_visible() and link.is_enabled():
                link.click()
                page.wait_for_load_state("networkidle")
                assert page.url != "about:blank"
                page.go_back()
                page.wait_for_load_state("networkidle")

    def test_external_links(self, page):
        """IN02-002: 外部链接"""
        external_links = page.locator("a[href^='http']:not([href*='tjjzcy.com'])")
        if external_links.count() > 0:
            with page.expect_popup() as popup_info:
                external_links.first.click()
            popup = popup_info.value
            assert popup.url.startswith("http")
            popup.close()
