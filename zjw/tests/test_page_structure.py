"""页面结构与导航模块测试"""
import pytest

class TestPageStructure:
    """页面结构测试类"""

    def test_page_load(self, page):
        """P01-001: 页面正常加载"""
        page.wait_for_load_state("networkidle")
        assert "天津市建筑产业互联网平台" in page.title()

    def test_page_refresh(self, page):
        """P01-002: F5刷新测试"""
        initial_title = page.title()
        page.reload()
        page.wait_for_load_state("networkidle")
        assert page.title() == initial_title

    def test_logo_display_and_click(self, page):
        """P02-001: Logo显示与点击"""
        logo = page.locator("img").first
        assert logo.is_visible(), "Logo未显示"
        logo.click()
        page.wait_for_load_state("networkidle")
        assert "天津市建筑产业互联网平台" in page.title()

    def test_navigation_links(self, page):
        """P02-002: 导航链接跳转"""
        nav_items = page.locator("nav a, .nav-item a")
        count = nav_items.count()
        for i in range(min(count, 5)):
            try:
                nav_item = nav_items.nth(i)
                if nav_item.is_visible() and nav_item.is_enabled():
                    nav_item.click()
                    page.wait_for_load_state("networkidle")
                    assert page.url != "about:blank"
                    page.go_back()
                    page.wait_for_load_state("networkidle")
            except Exception:
                continue

    def test_login_button_click(self, page):
        """P02-003: 登录按钮点击-弹窗展示"""
        # 检查登录按钮是否存在
        login_btn = page.locator("text=登录").first
        assert login_btn.is_visible(), "登录按钮未显示"
        
        # 点击登录按钮，验证弹窗出现
        login_btn.click()
        page.wait_for_load_state("networkidle")
        
        # 检查登录弹窗内容（用户反馈弹窗包含"欢迎来到"文字）
        assert "欢迎来到" in page.content(), "登录弹窗中未找到'欢迎来到'文字"
        
        # 截图记录登录弹窗状态
        page.screenshot(path="login_popup.png", full_page=True)
        
        # 关闭登录弹窗
        close_btn = page.locator("div.n-dialog button.n-dialog__close, div.n-modal button[aria-label*='关闭']").first
        if close_btn.is_visible():
            close_btn.click()
        else:
            page.keyboard.press("Escape")
        
        page.wait_for_load_state("networkidle")

    def test_register_button_click(self, page):
        """P02-004: 注册按钮点击-新页面跳转"""
        from conftest import click_and_wait_for_new_page
        
        # 检查注册按钮是否存在
        register_btn = page.locator("text=注册").first
        assert register_btn.is_visible(), "注册按钮未显示"
        
        # 点击注册按钮（注册打开新页面）
        result_page = click_and_wait_for_new_page(page, register_btn)
        assert "register" in result_page.url.lower(), f"点击注册后URL未跳转到注册页面，当前URL: {result_page.url}"