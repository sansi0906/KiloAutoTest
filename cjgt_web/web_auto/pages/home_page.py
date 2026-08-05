# -*- coding: utf-8 -*-
"""首页 / 导航页面对象 —— 负责各模块导航"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    """首页导航"""

    # 各模块路径
    PATHS = {
        "service_project": "/smart-service/project-config",
        "contract_service": "/smart-service/contract-service",
        "knowledge": "/content-manage/knowledge",
    }

    def __init__(self, page: Page):
        super().__init__(page)

    def goto_service_project(self) -> None:
        """导航到服务项目配置"""
        self.navigate(self.PATHS["service_project"])

    def goto_contract_service(self) -> None:
        """导航到合同服务配置"""
        self.navigate(self.PATHS["contract_service"])

    def goto_knowledge(self) -> None:
        """导航到知识库"""
        self.navigate(self.PATHS["knowledge"])
