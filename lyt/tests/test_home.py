"""
乐云泰App自动化测试 - 首页模块测试用例
"""
import pytest
import time


class TestHome:
    def test_01_home_visible(self, app, home):
        """首页Tab可见"""
        app.go_tab("home")
        assert home.is_visible(), "首页Tab不可见"
        app.dm.screenshot("home_01_visible")

    def test_02_home_elements(self, app, home):
        """首页元素检查"""
        app.go_tab("home")
        elements = home.get_home_elements()
        assert len(elements) > 0, "首页无内容"
        app.dm.screenshot("home_02_elements")

    def test_03_scroll_down(self, app, home):
        """首页下滑"""
        app.go_tab("home")
        home.scroll_to_bottom()
        app.dm.screenshot("home_03_scroll_down")

    def test_04_scroll_up(self, app, home):
        """首页上滑"""
        app.go_tab("home")
        home.scroll_to_top()
        app.dm.screenshot("home_04_scroll_up")

    def test_05_search(self, app, home):
        """首页搜索"""
        app.go_tab("home")
        result = home.search("消防")
        app.dm.screenshot("home_05_search")
