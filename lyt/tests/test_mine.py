"""
乐云泰App自动化测试 - 我的模块测试用例
"""
import pytest
import time


class TestMine:
    def test_01_mine_visible(self, app, mine):
        """我的Tab可见"""
        app.go_tab("mine")
        assert mine.is_visible(), "我的Tab不可见"
        app.dm.screenshot("mine_01_visible")

    def test_02_user_info(self, app, mine):
        """用户信息"""
        app.go_tab("mine")
        info = mine.get_user_info()
        assert len(info) > 0, "我的页面无内容"
        app.dm.screenshot("mine_02_info")

    def test_03_login_status(self, app, mine):
        """登录状态检查"""
        app.go_tab("mine")
        result = mine.check_login_status()
        app.dm.screenshot("mine_03_status")

    def test_04_menu_items(self, app, mine):
        """菜单项遍历"""
        app.go_tab("mine")
        menu_items = ["账号管理", "地址管理", "我的收藏", "浏览历史", "客户服务", "关于我们", "设置"]
        for item in menu_items:
            if app.d(text=item).exists(timeout=1):
                app.dm.screenshot(f"mine_menu_{item}")

    def test_05_scroll_mine(self, app, mine):
        """我的页面滑动"""
        app.go_tab("mine")
        app.scroll_down()
        app.dm.screenshot("mine_05_scroll")
