# -*- coding: utf-8 -*-
"""服务项目配置页面对象"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ServiceProjectPage(BasePage):
    """智能服务配置 - 服务项目配置"""

    def __init__(self, page: Page):
        super().__init__(page)

    def open_add_modal(self) -> bool:
        """点击新增服务项目按钮，打开弹窗"""
        selectors = [
            'button:has-text("新增服务项目")',
            'button:has-text("新增")',
            '.ant-btn-primary:has-text("新增")',
        ]
        for sel in selectors:
            btn = self.page.locator(sel)
            if btn.count() > 0:
                btn.first.click()
                self.page.wait_for_timeout(1500)
                logger.info("点击新增服务项目按钮")
                return self.wait_modal()
        logger.warning("未找到新增按钮")
        return False

    def fill_form(self, name: str, subtitle: str, content: str) -> None:
        """填写服务项目表单"""
        form_info = self.get_modal_form_fields()

        # 填写服务项目名称
        if form_info["inputs"]:
            self.fill_input_by_id(form_info["inputs"][0]["id"], name)
            logger.info("填写服务项目名称")

        # 填写副标题
        if len(form_info["inputs"]) > 1:
            self.fill_input_by_id(form_info["inputs"][1]["id"], subtitle)
            logger.info("填写副标题")

        # 填写服务项目介绍（隐藏 textarea）
        for ta in form_info["textareas"]:
            if ta["id"]:
                self.fill_hidden_textarea(ta["id"], content)
                logger.info(f"填写服务项目介绍 (id={ta['id']})")
                break

        # 选择计费方式 radio
        self.select_first_radio_if_unchecked()
        logger.info("表单填写完成")

    def submit_and_verify(self, name: str) -> tuple:
        """
        提交表单并验证

        Returns:
            (success: bool, toast_messages: list)
        """
        self.submit_modal()
        msgs = self.get_toasts()
        errors = self.get_form_errors()
        logger.info(f"Toast: {msgs}, Errors: {errors}")

        if errors:
            return False, errors

        if self.is_data_in_table(name):
            return True, msgs
        return False, msgs

    def has_edit_button(self) -> bool:
        """是否存在编辑按钮"""
        return (
            self.page.locator(
                'button:has-text("编辑"), a:has-text("编辑")'
            ).count()
            > 0
        )

    def click_edit(self) -> bool:
        """点击编辑按钮"""
        btn = self.page.locator(
            'button:has-text("编辑"), a:has-text("编辑")'
        )
        if btn.count() > 0:
            btn.first.click()
            self.page.wait_for_timeout(1500)
            return self.wait_modal()
        return False

    def has_switch(self) -> bool:
        """是否存在展示切换按钮（"不展示"/"展示"）"""
        return (
            self.page.locator(
                'button:has-text("不展示"), button:has-text("展示"), .ant-switch'
            ).count()
            > 0
        )

    def toggle_switch(self) -> list:
        """切换展示状态，返回 toast"""
        btn = self.page.locator(
            'button:has-text("不展示"), button:has-text("展示"), .ant-switch'
        )
        btn.first.click()
        self.page.wait_for_timeout(2000)

        # 可能有二次确认弹窗
        confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
        if confirm.count() > 0:
            confirm.first.click()
            self.page.wait_for_timeout(2000)
        return self.get_toasts()
