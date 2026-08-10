# -*- coding: utf-8 -*-
"""服务定价配置页面对象"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class ProjectPricePage(BasePage):
    """智能服务配置 - 服务定价配置"""

    def __init__(self, page: Page):
        super().__init__(page)

    # ──────────── 导航 ────────────

    def goto(self) -> None:
        """导航到服务定价配置页"""
        self.navigate("/smart-service/project-price")

    # ──────────── Tab 操作 ────────────

    def get_tabs(self) -> list:
        """获取所有 Tab 名称"""
        tabs = self.page.evaluate("""
            () => {
                const tabs = document.querySelectorAll('.ant-tabs-tab');
                return Array.from(tabs).map(t => t.textContent.trim());
            }
        """)
        logger.info(f"所有 Tab: {tabs}")
        return tabs

    def switch_tab(self, tab_name: str) -> bool:
        """切换到指定 Tab（如果已激活则跳过点击）"""
        active = self.get_active_tab()
        if active == tab_name:
            logger.info(f"Tab '{tab_name}' 已激活，跳过切换")
            return True
        tab = self.page.locator(f'.ant-tabs-tab:has-text("{tab_name}")')
        if tab.count() > 0:
            tab.first.click(force=True)
            self.page.wait_for_timeout(1500)
            logger.info(f"切换到 Tab: {tab_name}")
            return True
        logger.warning(f"未找到 Tab: {tab_name}")
        return False

    def switch_tab_by_index(self, index: int) -> bool:
        """切换到指定索引的 Tab（通过索引更可靠，避免文本匹配歧义）"""
        tabs = self.page.locator(".ant-tabs-tab")
        count = tabs.count()
        if count > index:
            tabs.nth(index).click(force=True)
            self.page.wait_for_timeout(1500)
            logger.info(f"切换到索引 {index} 的 Tab (共 {count} 个)")
            return True
        logger.warning(f"Tab 索引 {index} 不存在 (共 {count} 个)")
        return False

    def get_active_tab(self) -> str:
        """获取当前激活的 Tab 名称"""
        active = self.page.evaluate("""
            () => {
                const tab = document.querySelector('.ant-tabs-tab-active');
                return tab ? tab.textContent.trim() : '';
            }
        """)
        return active

    # ──────────── 表格 / 定价内容 ────────────

    def get_table_headers(self) -> list:
        """获取定价表格列头"""
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
        """获取当前 Tab 下定价数据行数"""
        return self.page.locator(".ant-table-tbody tr.ant-table-row").count()

    def get_pricing_regions(self) -> list:
        """获取当前 Tab 下所有地区名称列表"""
        return self.page.evaluate("""
            () => {
                const rows = document.querySelectorAll('.ant-table-tbody tr.ant-table-row');
                const regions = [];
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length > 0) {
                        const text = cells[0].textContent.trim();
                        if (text) regions.push(text);
                    }
                });
                return regions;
            }
        """)

    def has_pricing_data(self) -> bool:
        """当前 Tab 是否有定价数据"""
        return self.get_table_row_count() > 0

    # ──────────── 操作按钮 ────────────

    def download_template(self) -> bool:
        """点击下载服务定价模板"""
        btn = self.page.locator('button:has-text("下载服务定价模板"), a:has-text("下载服务定价模板")')
        if btn.count() == 0:
            btn = self.page.locator('.ant-btn:has-text("下载")')
        if btn.count() > 0:
            with self.page.expect_download(timeout=10000) as dl_info:
                btn.first.click()
            download = dl_info.value
            logger.info(f"下载模板: {download.suggested_filename if download else 'None'}")
            return download is not None
        logger.warning("未找到下载模板按钮")
        return False

    def has_import_button(self) -> bool:
        """是否存在导入价格按钮"""
        return self.page.locator('button:has-text("导入"), .ant-btn:has-text("导入")').count() > 0

    def has_download_button(self) -> bool:
        """是否存在下载模板按钮"""
        return self.page.locator(
            'button:has-text("下载服务定价模板"), a:has-text("下载服务定价模板")'
        ).count() > 0

    def click_import_button(self) -> bool:
        """点击导入按钮，打开导入弹窗"""
        btn = self.page.locator('button:has-text("导入"), .ant-btn:has-text("导入")')
        if btn.count() > 0:
            btn.first.click()
            self.page.wait_for_timeout(1000)
            logger.info("点击导入按钮")
            return self.wait_modal(timeout=3000)
        logger.warning("未找到导入按钮")
        return False

    def upload_import_file(self, file_path: str) -> bool:
        """上传导入文件"""
        try:
            # 直接设置文件输入，不需要监听 filechooser 事件
            upload_btn = self.page.locator(
                '.ant-modal input[type="file"], .ant-upload-btn input[type="file"]'
            ).first
            upload_btn.set_input_files(file_path)
            self.page.wait_for_timeout(2000)
            logger.info(f"上传文件: {file_path}")
            return True
        except Exception as e:
            logger.warning(f"文件上传失败: {e}")
            return False

    def click_import_confirm(self) -> list:
        """点击导入弹窗的确认按钮"""
        confirm = self.page.locator(
            '.ant-modal button:has-text("确 定"), .ant-modal button:has-text("确 认")'
        )
        if confirm.count() > 0:
            confirm.first.click()
            self.page.wait_for_timeout(3000)
        return self.get_toasts()

    def has_imported_file_name(self, name: str) -> bool:
        """检查上传的文件名是否显示在弹窗中"""
        return self.page.evaluate(
            """(name) => {
                return document.body.textContent.includes(name);
            }""",
            name
        )

    def get_download_filename(self) -> str:
        """获取下载的文件名（用于验证下载的文件）"""
        return self._last_download_filename if hasattr(self, '_last_download_filename') else ""
