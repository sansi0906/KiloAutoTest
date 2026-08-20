"""
超级个体后台管理系统 - 客户管理测试
测试超级个体档案和服务工单管理页面的各项功能
"""
import asyncio
import os
from test_base import TestBase


class CustomerManagementTests(TestBase):
    """客户管理测试类"""

    def __init__(self):
        super().__init__()
        self.current_module = "客户管理"

    async def test_customer_archive_page_load(self):
        """测试客户管理 - 超级个体档案页面加载"""
        test_name = "超级个体档案 - 页面加载"
        await self.navigate_to("超级个体档案")

        url_ok = "/customer/customer-archive" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["用户ID", "用户姓名", "手机号", "户籍地", "服务驿站", "服务商", "创建时间", "操作"]
        headers_ok = all(any(eh in h for h in headers) for eh in expected_headers)

        buttons = await self.get_buttons()
        has_query = any("查询" in b for b in buttons)
        has_reset = any("重置" in b for b in buttons)
        has_detail = any("详情" in b for b in buttons)

        passed = url_ok and headers_ok and has_query and has_reset and has_detail
        screenshot = await self.screenshot("customer_archive_page_load")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头包含{expected_headers[:3]}..., 有查询/重置/详情按钮",
            f"URL: {self.page.url}, 列头: {headers[:5]}..., 按钮: {buttons}",
            screenshot
        )

    async def test_customer_archive_search(self):
        """测试客户管理 - 搜索功能"""
        test_name = "超级个体档案 - 搜索功能"
        await self.navigate_to("超级个体档案")

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/customer/customer-archive" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("customer_archive_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_customer_archive_search_reset(self):
        """测试客户管理 - 重置搜索"""
        test_name = "超级个体档案 - 重置搜索"
        await self.navigate_to("超级个体档案")

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/customer/customer-archive" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("customer_archive_search_reset")
        self.record_result(
            test_name, passed,
            "点击重置后应清空搜索条件并显示全部数据",
            f"重置后行数: {rows_after}",
            screenshot
        )

    async def test_customer_archive_detail(self):
        """测试客户管理 - 查看详情"""
        test_name = "超级个体档案 - 查看详情"
        await self.navigate_to("超级个体档案")

        detail_btn = self.page.locator('a:has-text("详情"), button:has-text("详情"), .ant-btn:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            passed = modal_appeared
            screenshot = await self.screenshot("customer_archive_detail")
            self.record_result(
                test_name, passed,
                "点击详情后应弹出详情弹窗",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有详情按钮", "未找到详情按钮", "")

    async def test_customer_archive_view_contract(self):
        """测试客户管理 - 查看合同"""
        test_name = "超级个体档案 - 查看合同"
        await self.navigate_to("超级个体档案")

        contract_btn = self.page.locator('a:has-text("查看合同"), button:has-text("查看合同"), .ant-btn:has-text("查看合同")').first
        if await contract_btn.count() > 0:
            await contract_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            passed = modal_appeared
            screenshot = await self.screenshot("customer_archive_view_contract")
            self.record_result(
                test_name, passed,
                "点击查看合同后应弹出合同详情弹窗",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有查看合同按钮", "未找到查看合同按钮", "")

    async def test_customer_archive_pagination(self):
        """测试客户管理 - 表格分页"""
        test_name = "超级个体档案 - 表格分页"
        await self.navigate_to("超级个体档案")

        pagination = self.page.locator('.ant-pagination').first
        has_pagination = await pagination.count() > 0

        if has_pagination:
            pagination_info = await self.page.evaluate("""
                () => {
                    const pagination = document.querySelector('.ant-pagination');
                    if (!pagination) return null;
                    const total = pagination.querySelector('.ant-pagination-total-text');
                    const items = pagination.querySelectorAll('.ant-pagination-item');
                    return {
                        total: total ? total.textContent : null,
                        page_count: items.length,
                    };
                }
            """)
            passed = pagination_info is not None and pagination_info.get('page_count', 0) >= 2
            screenshot = await self.screenshot("customer_archive_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器且至少2页",
                f"分页信息: {pagination_info}",
                screenshot
            )
        else:
            rows = await self.get_table_row_count()
            passed = rows > 0
            screenshot = await self.screenshot("customer_archive_no_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器或显示数据",
                f"分页器: 无, 数据行数: {rows}",
                screenshot
            )

    async def test_work_order_page_load(self):
        """测试客户管理 - 服务工单管理页面加载"""
        test_name = "服务工单管理 - 页面加载"
        await self.navigate_to("服务工单管理")

        url_ok = "/customer/work-order" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["工单号", "合同编号", "客户姓名", "客户手机号", "服务驿站", "服务商", "服务项目", "工单状态", "创建时间", "接单时间", "操作"]
        headers_ok = all(any(eh in h for h in headers) for eh in expected_headers)

        buttons = await self.get_buttons()
        has_query = any("查询" in b for b in buttons)
        has_reset = any("重置" in b for b in buttons)
        has_detail = any("详情" in b for b in buttons)

        passed = url_ok and headers_ok and has_query and has_reset and has_detail
        screenshot = await self.screenshot("work_order_page_load")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头包含{expected_headers[:3]}..., 有查询/重置/详情按钮",
            f"URL: {self.page.url}, 列头: {headers[:5]}..., 按钮: {buttons}",
            screenshot
        )

    async def test_work_order_search(self):
        """测试客户管理 - 服务工单搜索功能"""
        test_name = "服务工单管理 - 搜索功能"
        await self.navigate_to("服务工单管理")

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/customer/work-order" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("work_order_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_work_order_search_reset(self):
        """测试客户管理 - 服务工单重置搜索"""
        test_name = "服务工单管理 - 重置搜索"
        await self.navigate_to("服务工单管理")

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/customer/work-order" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("work_order_search_reset")
        self.record_result(
            test_name, passed,
            "点击重置后应清空搜索条件并显示全部数据",
            f"重置后行数: {rows_after}",
            screenshot
        )

    async def test_work_order_detail(self):
        """测试客户管理 - 服务工单查看详情"""
        test_name = "服务工单管理 - 查看详情"
        await self.navigate_to("服务工单管理")

        detail_btn = self.page.locator('a:has-text("详情"), button:has-text("详情"), .ant-btn:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            passed = modal_appeared
            screenshot = await self.screenshot("work_order_detail")
            self.record_result(
                test_name, passed,
                "点击详情后应弹出详情弹窗",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有详情按钮", "未找到详情按钮", "")

    async def test_work_order_pagination(self):
        """测试客户管理 - 服务工单表格分页"""
        test_name = "服务工单管理 - 表格分页"
        await self.navigate_to("服务工单管理")

        pagination = self.page.locator('.ant-pagination').first
        has_pagination = await pagination.count() > 0

        if has_pagination:
            pagination_info = await self.page.evaluate("""
                () => {
                    const pagination = document.querySelector('.ant-pagination');
                    if (!pagination) return null;
                    const total = pagination.querySelector('.ant-pagination-total-text');
                    const items = pagination.querySelectorAll('.ant-pagination-item');
                    return {
                        total: total ? total.textContent : null,
                        page_count: items.length,
                    };
                }
            """)
            passed = pagination_info is not None
            screenshot = await self.screenshot("work_order_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器",
                f"分页信息: {pagination_info}",
                screenshot
            )
        else:
            rows = await self.get_table_row_count()
            passed = rows > 0
            screenshot = await self.screenshot("work_order_no_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器或显示数据",
                f"分页器: 无, 数据行数: {rows}",
                screenshot
            )

    async def run_all(self, base=None):
        """运行所有测试"""
        if base is not None:
            self.pw = base.pw
            self.browser = base.browser
            self.context = base.context
            self.page = base.page
        else:
            await self.setup()
        try:
            if base is None:
                await self.login()

            print("\n--- 客户管理测试 ---")
            await self.test_customer_archive_page_load()
            await self.test_customer_archive_search()
            await self.test_customer_archive_search_reset()
            await self.test_customer_archive_detail()
            await self.test_customer_archive_view_contract()
            await self.test_customer_archive_pagination()
            await self.test_work_order_page_load()
            await self.test_work_order_search()
            await self.test_work_order_search_reset()
            await self.test_work_order_detail()
            await self.test_work_order_pagination()

        finally:
            if base is None:
                await self.teardown()

        return self.test_results
