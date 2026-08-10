# -*- coding: utf-8 -*-
"""服务商管理 - 代理记账公司管理页面对象"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ProviderPage(BasePage):
    """服务商管理 - 代理记账公司管理"""

    def __init__(self, page: Page):
        super().__init__(page)

    # ──────────── 导航 ────────────

    def goto(self) -> None:
        """导航到代理记账公司管理页"""
        self.navigate("/service-provider/proxy-accounting")

    # ──────────── 表格操作 ────────────

    def get_table_headers(self) -> list:
        """获取表格列头"""
        return self.page.evaluate("""
            () => {
                const thead = document.querySelector('.ant-table-thead');
                if (!thead) return [];
                return Array.from(thead.querySelectorAll('th'))
                    .map(th => th.textContent.trim())
                    .filter(t => t);
            }
        """)

    def get_table_row_count(self) -> int:
        """获取表格数据行数"""
        return self.page.locator(".ant-table-tbody tr.ant-table-row").count()

    def get_pagination_info(self) -> dict:
        """获取分页信息"""
        return self.page.evaluate("""
            () => {
                const p = document.querySelector('.ant-pagination');
                if (!p) return {exists: false};
                const total = p.querySelector('.ant-pagination-total-text');
                const active = p.querySelector('.ant-pagination-item-active');
                const items = p.querySelectorAll('.ant-pagination-item');
                return {
                    exists: true,
                    total: total ? total.textContent.trim() : '',
                    current: active ? active.textContent.trim() : '1',
                    page_count: items.length
                };
            }
        """)

    def has_search_box(self) -> bool:
        """检查是否存在搜索框"""
        return self.page.locator(
            "input[placeholder*='公司名称'], "
            "input[placeholder*='请输入'], "
            ".jeecg-table-search input"
        ).count() > 0

    def search(self, keyword: str, input_id: str = None) -> None:
        """搜索并回车"""
        if input_id:
            el = self.page.locator(f"#{input_id}")
        else:
            el = self.page.locator(
                "input[placeholder*='公司名称']"
            ).first
        el.fill(keyword)
        self.page.wait_for_timeout(500)
        el.press("Enter")
        self.page.wait_for_timeout(2000)
        logger.info(f"搜索: {keyword}")

    def clear_search(self, input_id: str = None) -> None:
        """清空搜索"""
        if input_id:
            el = self.page.locator(f"#{input_id}")
        else:
            el = self.page.locator(
                "input[placeholder*='公司名称']"
            ).first
        el.fill("")
        el.press("Enter")
        self.page.wait_for_timeout(2000)
        logger.info("清空搜索")

    # ──────────── 按钮操作 ────────────

    def has_add_button(self) -> bool:
        """是否存在服务商入驻按钮"""
        return self.page.locator(
            'button:has-text("服务商入驻"), button:has-text("新增"), button:has-text("添加")'
        ).count() > 0

    def click_add_button(self) -> bool:
        """点击服务商入驻按钮，打开弹窗"""
        btn = self.page.locator(
            'button:has-text("服务商入驻"), button:has-text("新增"), button:has-text("添加")'
        )
        if btn.count() > 0:
            btn.first.click()
            self.page.wait_for_timeout(1500)
            logger.info("点击服务商入驻按钮")
            return self.wait_modal()
        logger.warning("未找到服务商入驻按钮")
        return False

    def has_edit_button(self) -> bool:
        """检查是否存在编辑按钮"""
        return self.page.locator(
            '.ant-table-tbody button:has-text("编辑"), '
            '.ant-table-tbody a:has-text("编辑")'
        ).count() > 0

    def click_edit_first_row(self) -> bool:
        """点击第一行编辑按钮"""
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

    def has_detail_button(self) -> bool:
        """检查是否存在详情按钮"""
        return self.page.locator(
            '.ant-table-tbody button:has-text("详情"), '
            '.ant-table-tbody a:has-text("详情")'
        ).count() > 0

    def view_detail_first_row(self) -> bool:
        """点击第一行详情按钮"""
        btn = self.page.locator(
            '.ant-table-tbody button:has-text("详情"), '
            '.ant-table-tbody a:has-text("详情")'
        )
        if btn.count() == 0:
            return False
        btn.first.click()
        self.page.wait_for_timeout(1500)
        logger.info("点击详情按钮")
        return self.wait_modal(timeout=3000)

    def has_delete_button(self) -> bool:
        """检查是否存在删除/禁用按钮"""
        return self.page.locator(
            '.ant-table-tbody button:has-text("禁用"), '
            '.ant-table-tbody button:has-text("删除"), '
            '.ant-table-tbody a:has-text("禁用")'
        ).count() > 0

    def click_disable_first_row(self) -> bool:
        """点击第一行禁用按钮"""
        btn = self.page.locator(
            '.ant-table-tbody button:has-text("禁用"), '
            '.ant-table-tbody a:has-text("禁用")'
        )
        if btn.count() == 0:
            return False
        btn.first.click()
        self.page.wait_for_timeout(1000)
        logger.info("点击禁用按钮")
        return True

    def confirm_disable(self) -> list:
        """在禁用确认弹窗中点击确认"""
        confirm = self.page.locator(
            ".ant-popconfirm button.ant-btn-primary, "
            ".ant-modal-confirm .ant-btn-primary"
        )
        if confirm.count() > 0:
            confirm.first.click()
            self.page.wait_for_timeout(2000)
        return self.get_toasts()

    def cancel_disable(self) -> None:
        """在禁用确认弹窗中点击取消"""
        cancel = self.page.locator(
            ".ant-popconfirm button.ant-btn-default, "
            ".ant-popconfirm .ant-btn:not(.ant-btn-primary)"
        )
        if cancel.count() > 0:
            cancel.first.click()
            self.page.wait_for_timeout(1000)

    def has_reset_password_button(self) -> bool:
        """检查是否存在重置密码按钮"""
        return self.page.locator(
            '.ant-table-tbody button:has-text("重置密码"), '
            '.ant-table-tbody a:has-text("重置密码")'
        ).count() > 0

    def click_reset_password_first_row(self) -> bool:
        """点击第一行重置密码按钮"""
        btn = self.page.locator(
            '.ant-table-tbody button:has-text("重置密码"), '
            '.ant-table-tbody a:has-text("重置密码")'
        )
        if btn.count() == 0:
            return False
        btn.first.click()
        self.page.wait_for_timeout(1000)
        logger.info("点击重置密码按钮")
        return True

    # ──────────── 表单操作 ────────────

    def get_modal_required_fields(self) -> list:
        """获取弹窗内必填字段标签"""
        return self.page.evaluate("""
            () => {
                const modal = document.querySelector('.ant-modal');
                if (!modal) return [];
                const required = modal.querySelectorAll('.ant-form-item-required');
                return Array.from(required).map(r => {
                    const item = r.closest('.ant-form-item');
                    return item?.querySelector('.ant-form-item-label')?.textContent.trim() || '';
                }).filter(t => t);
            }
        """)

    def fill_form(
        self,
        company_name: str,
        office_address: str,
        contact_person: str,
        contact_phone: str,
        service_project: str = None,
        enable_status: str = None
    ) -> None:
        """
        填写服务商表单

        Args:
            company_name: 公司名称
            office_address: 办公地址
            contact_person: 联系人
            contact_phone: 联系电话
            service_project: 服务项目（可选）
            enable_status: 启用状态（可选）
        """
        def fill_by_codefield(codefield, value):
            result = self.page.evaluate("""
                (params) => {
                    const input = document.querySelector('.ant-modal input[codefield="' + params.codefield + '"]');
                    if (!input) return false;
                    input.value = params.value;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
            """, {"codefield": codefield, "value": value})
            return result

        # 1. 公司编号（可能自动生成，尝试填充）
        fill_by_codefield("companyNo", "100001300")
        logger.info("填写/检查公司编号")

        # 2. 公司名称
        fill_by_codefield("companyName", company_name)
        logger.info("填写公司名称")

        # 3. 统一社会信用代码
        fill_by_codefield("creditCode", "9119XX17495546358")
        logger.info("填写统一社会信用代码")

        # 4. 办公地址
        fill_by_codefield("officeAddress", office_address)
        logger.info("填写办公地址")

        # 5. 服务区域（级联选择）
        self.select_dropdown("服务区域", 0)
        logger.info("选择服务区域")

        # 6. 服务项目（下拉选择）
        if service_project:
            self.select_dropdown("服务项目", 0)
            logger.info("选择服务项目")

        # 7. 联系人
        fill_by_codefield("contactPerson", contact_person)
        logger.info("填写联系人")

        # 8. 联系电话
        fill_by_codefield("contactPhone", contact_phone)
        logger.info("填写联系电话")

        # 9. 启用状态
        if enable_status:
            self.select_dropdown("启用状态", 0)
            logger.info("选择启用状态")

        logger.info("表单填写完成")

    def submit_modal(self) -> None:
        """点击弹窗内的确认按钮"""
        self.page.click('.ant-modal button:has-text("确 定"), .ant-modal button:has-text("确 认")')
        self.page.wait_for_timeout(3000)

    def submit_and_verify(self, company_name: str) -> tuple:
        """提交并验证"""
        self.submit_modal()
        msgs = self.get_toasts()
        errors = self.get_form_errors()
        logger.info(f"Toast: {msgs}, Errors: {errors}")

        if errors:
            return False, errors
        if self.is_data_in_table(company_name):
            return True, msgs
        return False, msgs

    def is_data_in_table(self, keyword: str) -> bool:
        """检查数据是否在表格中"""
        self.page.reload(wait_until="networkidle")
        self.page.wait_for_timeout(2000)
        text = self.page.evaluate(
            "() => document.querySelector('.ant-table-tbody')?.textContent || ''"
        )
        return keyword in text
