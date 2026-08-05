# -*- coding: utf-8 -*-
"""合同服务配置页面对象"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ContractServicePage(BasePage):
    """智能服务配置 - 合同服务配置"""

    def __init__(self, page: Page):
        super().__init__(page)

    def open_add_modal(self) -> bool:
        """点击新增合同服务按钮，打开弹窗"""
        # 等待 loading 消失
        self.wait_loading()
        self.page.click('button:has-text("新增合同服务")')
        self.page.wait_for_timeout(1500)
        logger.info("点击新增合同服务按钮")
        return self.wait_modal()

    def fill_form(
        self, title: str, content: str, fee: str
    ) -> None:
        """
        填写合同服务表单

        Args:
            title: 合同服务标题
            content: 合同服务内容
            fee: 费用内容
        """
        # 1. 合同服务标题
        if not self.fill_input_by_id("ContractServiceForm_title", title):
            self.page.locator('input[codefield="title"]').fill(title)
        logger.info("填写合同服务标题")

        # 2. 所属服务项目 - 下拉选择
        self.select_dropdown("所属服务项目", 0)
        logger.info("选择所属服务项目")

        # 3. 合同服务内容
        if not self.fill_textarea_by_id("ContractServiceForm_content", content):
            self.page.locator('textarea[codefield="content"]').fill(content)
        logger.info("填写合同服务内容")

        # 4. 费用内容
        if not self.fill_textarea_by_id("ContractServiceForm_priceContent", fee):
            self.page.locator('textarea[codefield="priceContent"]').fill(fee)
        logger.info("填写费用内容")

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

    def has_edit_button(self) -> bool:
        """检查是否存在编辑按钮"""
        return self.page.locator(
            '.ant-table-tbody button:has-text("编辑"), '
            '.ant-table-tbody a:has-text("编辑")'
        ).count() > 0

    def click_edit_first_row(self) -> bool:
        """点击第一行的编辑按钮"""
        btn = self.page.locator(
            '.ant-table-tbody button:has-text("编辑"), '
            '.ant-table-tbody a:has-text("编辑")'
        )
        if btn.count() == 0:
            return False
        btn.first.click()
        self.page.wait_for_timeout(1500)
        logger.info("点击编辑按钮")
        return self.wait_modal()

    def has_delete_button(self) -> bool:
        """检查是否存在删除按钮"""
        return self.page.locator(
            '.ant-table-tbody button:has-text("删除"), '
            '.ant-table-tbody a:has-text("删除")'
        ).count() > 0
