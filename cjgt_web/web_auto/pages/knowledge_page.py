# -*- coding: utf-8 -*-
"""知识库页面对象"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class KnowledgePage(BasePage):
    """内容管理 - 知识库"""

    def __init__(self, page: Page):
        super().__init__(page)

    def open_add_modal(self) -> bool:
        """点击新增知识库按钮，打开弹窗"""
        self.page.click('button:has-text("新增知识库")')
        self.page.wait_for_timeout(1500)
        logger.info("点击新增知识库按钮")
        return self.wait_modal()

    def fill_form(self, title: str, content: str) -> None:
        """
        填写知识库表单

        Args:
            title: 标题
            content: 内容（HTML 格式）
        """
        # 1. 标题
        self.fill_input_by_id("KnowledgeForm_title", title)
        logger.info("填写标题")

        # 2. 资讯类型 - 下拉
        self.select_dropdown("资讯类型", 0)
        logger.info("选择资讯类型")

        # 3. 展示位置 - 下拉
        self.select_dropdown("展示位置", 0)
        logger.info("选择展示位置")

        # 4. 适用区域 - 级联选择（多选）
        self.page.wait_for_timeout(500)
        self.select_dropdown("适用区域", 0)
        logger.info("选择适用区域")

        # 5. 内容 - TinyMCE 富文本编辑器
        self.page.wait_for_timeout(500)
        self.fill_tinymce_editor(content)
        logger.info("填写内容")

        logger.info("表单填写完成")

    def submit_and_verify(self, title: str) -> tuple:
        """提交并验证"""
        self.submit_modal()
        msgs = self.get_toasts()
        errors = self.get_form_errors()
        logger.info(f"Toast: {msgs}, Errors: {errors}")

        if errors:
            return False, errors
        if self.is_data_in_table(title):
            return True, msgs
        return False, msgs

    def has_toggle_button(self) -> bool:
        """是否存在禁用/启用按钮"""
        return (
            self.page.locator(
                'button:has-text("禁用"), button:has-text("启用"), '
                'a:has-text("禁用"), a:has-text("启用")'
            ).count()
            > 0
        )

    def toggle_status(self) -> tuple:
        """切换状态，返回 (按钮文本, toast)"""
        toggle = self.page.locator(
            'button:has-text("禁用"), button:has-text("启用"), '
            'a:has-text("禁用"), a:has-text("启用")'
        )
        text = toggle.first.text_content() or ""
        toggle.first.click()
        self.page.wait_for_timeout(1000)

        confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
        if confirm.count() > 0:
            confirm.first.click()
            self.page.wait_for_timeout(2000)
            return text, self.get_toasts()
        return text, []

    def has_detail_button(self) -> bool:
        """是否存在详情按钮"""
        return (
            self.page.locator(
                'button:has-text("详情"), a:has-text("详情")'
            ).count()
            > 0
        )

    def view_detail(self) -> bool:
        """查看详情，返回是否打开"""
        self.page.locator(
            'button:has-text("详情"), a:has-text("详情")'
        ).first.click()
        self.page.wait_for_timeout(1500)
        return (
            self.page.locator(".ant-modal, .ant-drawer").count() > 0
        )

    def close_detail(self) -> None:
        """关闭详情弹窗"""
        close_btn = self.page.locator(".ant-modal-close, .ant-drawer-close")
        if close_btn.count() > 0:
            close_btn.first.click()
            self.page.wait_for_timeout(500)
