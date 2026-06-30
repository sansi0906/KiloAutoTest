"""产业化服务模块测试"""
import pytest

class TestIndustrialService:
    """产业化服务测试类"""

    def test_industrial_service_module_exists(self, page):
        """I01-001: 产业化服务模块存在"""
        service_section = page.locator("text=专属客服").first
        if not service_section.is_visible():
            service_section = page.locator("text=产业化服务").first
        assert service_section.is_visible(), "产业化服务模块未显示"
        assert "专属客服" in page.content()
