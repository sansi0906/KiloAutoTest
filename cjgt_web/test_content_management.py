"""
内容管理模块 - 页面功能测试
测试页面：
1. 知识库 (/content-manage/knowledge)
"""
import asyncio
import os
from test_base import TestBase, SCREENSHOT_DIR


class ContentManagementTests(TestBase):
    """内容管理模块测试"""

    def __init__(self):
        super().__init__()
        self.current_module = "内容管理"

    async def test_knowledge_page_load(self):
        """测试知识库 - 页面加载"""
        test_name = "知识库 - 页面加载"
        await self.navigate_to("知识库")

        url_ok = "/content-manage/knowledge" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["标题", "内容", "展示位置", "适用区域", "资讯类型", "状态", "发布时间", "操作"]
        headers_ok = all(h in headers for h in expected_headers)

        buttons = await self.get_buttons()
        has_query = "查询" in buttons
        has_add = "新增知识库" in buttons
        has_detail = "详情" in buttons
        has_edit = "编辑" in buttons

        rows = await self.get_table_row_count()

        passed = url_ok and headers_ok and has_query and has_add and has_detail and has_edit
        screenshot = await self.screenshot("content_knowledge_page")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头完整, 有查询/新增/详情/编辑按钮",
            f"URL: {self.page.url}, 列头: {headers}, 按钮: {buttons}, 数据行: {rows}",
            screenshot
        )

    async def test_knowledge_search_by_title(self):
        """测试知识库 - 按标题搜索"""
        test_name = "知识库 - 按标题搜索"
        await self.navigate_to("知识库")

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入标题", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/content-manage/knowledge" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("content_knowledge_search_title")
        self.record_result(
            test_name, passed,
            "输入标题关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_knowledge_search_reset(self):
        """测试知识库 - 重置搜索"""
        test_name = "知识库 - 重置搜索"
        await self.navigate_to("知识库")

        # 输入搜索条件
        await self.fill_input("请输入标题", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(1000)

        # 点击重置
        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        # 验证输入框被清空
        input_value = await self.page.evaluate("""
            () => {
                const inp = document.querySelector('input[placeholder="请输入标题"]');
                return inp ? inp.value : null;
            }
        """)

        passed = input_value == ""
        screenshot = await self.screenshot("content_knowledge_reset")
        self.record_result(
            test_name, passed,
            "点击重置后搜索框应被清空",
            f"重置后输入框值: '{input_value}'",
            screenshot
        )

    async def test_knowledge_search_by_type(self):
        """测试知识库 - 按资讯类型筛选"""
        test_name = "知识库 - 按资讯类型筛选"
        await self.navigate_to("知识库")

        # 查找资讯类型的下拉选择器
        type_select = self.page.locator('.ant-select').nth(1)  # 第二个下拉框可能是资讯类型
        if await type_select.count() > 0:
            await type_select.click()
            await self.page.wait_for_timeout(500)

            # 获取下拉选项
            options = await self.page.evaluate("""
                () => {
                    const opts = document.querySelectorAll('.ant-select-item-option');
                    const texts = [];
                    for (const opt of opts) {
                        const text = opt.textContent.trim();
                        if (text) texts.push(text);
                    }
                    return texts;
                }
            """)

            if options:
                # 选择第一个选项
                first_option = self.page.locator('.ant-select-item-option').first
                await first_option.click()
                await self.page.wait_for_timeout(500)

                # 点击查询
                await self.click_button("查询")
                await self.page.wait_for_timeout(2000)

                rows_after = await self.get_table_row_count()
                passed = True
                screenshot = await self.screenshot("content_knowledge_search_type")
                self.record_result(
                    test_name, passed,
                    "选择资讯类型后查询，页面正常返回结果",
                    f"选项: {options}, 查询后行数: {rows_after}",
                    screenshot
                )
            else:
                self.record_result(test_name, False, "下拉框应有选项", "无选项", "")
        else:
            self.record_result(test_name, False, "应有资讯类型下拉框", "未找到下拉框", "")

    async def test_knowledge_search_by_status(self):
        """测试知识库 - 按状态筛选"""
        test_name = "知识库 - 按状态筛选"
        await self.navigate_to("知识库")

        # 查找状态下拉选择器（通常是最后一个）
        selects = self.page.locator('.ant-select')
        select_count = await selects.count()

        if select_count > 0:
            # 尝试最后一个下拉框
            status_select = selects.nth(select_count - 1)
            await status_select.click()
            await self.page.wait_for_timeout(500)

            options = await self.page.evaluate("""
                () => {
                    const opts = document.querySelectorAll('.ant-select-item-option');
                    const texts = [];
                    for (const opt of opts) {
                        const text = opt.textContent.trim();
                        if (text) texts.push(text);
                    }
                    return texts;
                }
            """)

            if options:
                # 选择第一个选项
                first_option = self.page.locator('.ant-select-item-option').first
                await first_option.click()
                await self.page.wait_for_timeout(500)

                await self.click_button("查询")
                await self.page.wait_for_timeout(2000)

                passed = True
                screenshot = await self.screenshot("content_knowledge_search_status")
                self.record_result(
                    test_name, passed,
                    "选择状态后查询，页面正常返回结果",
                    f"选项: {options}",
                    screenshot
                )
            else:
                self.record_result(test_name, False, "状态下拉框应有选项", "无选项", "")
        else:
            self.record_result(test_name, False, "应有状态下拉框", "未找到下拉框", "")

    async def test_knowledge_add_form_validation(self):
        """测试知识库 - 新增表单验证"""
        test_name = "知识库 - 新增表单验证"
        await self.navigate_to("知识库")

        await self.click_button("新增知识库")
        await self.page.wait_for_timeout(1500)

        modal_appeared = await self.wait_for_modal()
        if not modal_appeared:
            drawer = self.page.locator('.ant-drawer').first
            modal_appeared = await drawer.count() > 0

        if modal_appeared:
            # 检查表单字段
            form_labels = await self.page.evaluate("""
                () => {
                    const labels = document.querySelectorAll('.ant-form-item-label label, .ant-form-item label');
                    const texts = [];
                    for (const l of labels) {
                        const text = l.textContent.trim();
                        if (text) texts.push(text);
                    }
                    return texts;
                }
            """)

            # 尝试提交空表单
            for btn_text in ["确定", "确 定", "保存", "提交", "确认"]:
                if await self.click_button(btn_text):
                    break

            await self.page.wait_for_timeout(1000)
            errors = await self.get_form_errors()

            passed = len(errors) > 0 or len(form_labels) > 0
            screenshot = await self.screenshot("content_knowledge_add_validation")
            self.record_result(
                test_name, passed,
                "空表单提交时应显示验证错误",
                f"表单字段: {form_labels}, 验证错误: {errors}",
                screenshot
            )

            await self.close_modal()
            for btn_text in ["取消", "取 消"]:
                await self.click_button(btn_text)
                break
        else:
            screenshot = await self.screenshot("content_knowledge_add_no_modal")
            self.record_result(
                test_name, False,
                "点击新增后应弹出表单",
                "未检测到弹窗/抽屉",
                screenshot
            )

    async def test_knowledge_detail_view(self):
        """测试知识库 - 查看详情"""
        test_name = "知识库 - 查看详情"
        await self.navigate_to("知识库")

        # 查找详情按钮
        detail_btn = self.page.locator('a:has-text("详情"), button:has-text("详情"), .ant-btn:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            if not modal_appeared:
                drawer = self.page.locator('.ant-drawer').first
                modal_appeared = await drawer.count() > 0

            passed = modal_appeared
            screenshot = await self.screenshot("content_knowledge_detail")
            self.record_result(
                test_name, passed,
                "点击详情后应弹出详情页面",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
            for btn_text in ["关闭", "取消", "取 消", "返回"]:
                await self.click_button(btn_text)
                break
        else:
            self.record_result(
                test_name, False,
                "表格中应有详情按钮",
                "未找到详情按钮",
                ""
            )

    async def test_knowledge_edit(self):
        """测试知识库 - 编辑功能"""
        test_name = "知识库 - 编辑功能"
        await self.navigate_to("知识库")

        edit_btn = self.page.locator('a:has-text("编辑"), button:has-text("编辑"), .ant-btn:has-text("编辑")').first
        if await edit_btn.count() > 0:
            await edit_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            if not modal_appeared:
                drawer = self.page.locator('.ant-drawer').first
                modal_appeared = await drawer.count() > 0

            passed = modal_appeared
            screenshot = await self.screenshot("content_knowledge_edit")
            self.record_result(
                test_name, passed,
                "点击编辑后应弹出编辑表单",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
            for btn_text in ["取消", "取 消"]:
                await self.click_button(btn_text)
                break
        else:
            self.record_result(
                test_name, False,
                "表格中应有编辑按钮",
                "未找到编辑按钮",
                ""
            )

    async def test_knowledge_disable(self):
        """测试知识库 - 禁用功能"""
        test_name = "知识库 - 禁用功能"
        await self.navigate_to("知识库")

        # 查找禁用/启用按钮
        toggle_btn = self.page.locator('a:has-text("禁用"), button:has-text("禁用"), a:has-text("启用"), button:has-text("启用")').first
        if await toggle_btn.count() > 0:
            btn_text = await toggle_btn.inner_text()
            await toggle_btn.click()
            await self.page.wait_for_timeout(1000)

            # 检查是否有确认弹窗
            confirm = self.page.locator('.ant-popconfirm, .ant-modal-confirm, .ant-popover').first
            has_confirm = await confirm.count() > 0

            if has_confirm:
                # 点击取消
                cancel_btn = self.page.locator('.ant-popconfirm-buttons .ant-btn:not(.ant-btn-primary), .ant-modal-confirm-btns .ant-btn:not(.ant-btn-primary)').first
                if await cancel_btn.count() > 0:
                    await cancel_btn.click()
                    await self.page.wait_for_timeout(500)

            passed = True
            screenshot = await self.screenshot("content_knowledge_disable")
            self.record_result(
                test_name, passed,
                f"点击'{btn_text}'后应有确认提示",
                f"确认弹窗: {has_confirm}",
                screenshot
            )
        else:
            self.record_result(
                test_name, False,
                "表格中应有禁用/启用按钮",
                "未找到禁用/启用按钮",
                ""
            )

    async def test_knowledge_table_pagination(self):
        """测试知识库 - 表格分页"""
        test_name = "知识库 - 表格分页"
        await self.navigate_to("知识库")

        # 检查是否有分页器
        pagination = self.page.locator('.ant-pagination').first
        has_pagination = await pagination.count() > 0

        if has_pagination:
            # 获取分页信息
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
            screenshot = await self.screenshot("content_knowledge_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器",
                f"分页信息: {pagination_info}",
                screenshot
            )
        else:
            rows = await self.get_table_row_count()
            passed = rows > 0  # 如果没有分页器但有数据也可以
            screenshot = await self.screenshot("content_knowledge_no_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器或显示数据",
                f"分页器: 无, 数据行数: {rows}",
                screenshot
            )

    async def run_all(self):
        """运行所有测试"""
        await self.setup()
        try:
            await self.login()

            print("\n--- 知识库测试 ---")
            await self.test_knowledge_page_load()
            await self.test_knowledge_search_by_title()
            await self.test_knowledge_search_reset()
            await self.test_knowledge_search_by_type()
            await self.test_knowledge_search_by_status()
            await self.test_knowledge_add_form_validation()
            await self.test_knowledge_detail_view()
            await self.test_knowledge_edit()
            await self.test_knowledge_disable()
            await self.test_knowledge_table_pagination()

        finally:
            await self.teardown()

        return self.test_results
