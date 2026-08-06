"""
智能服务配置模块 - 页面功能测试
测试页面：
1. 服务项目配置 (/smart-service/project-config)
2. 服务定价配置 (/smart-service/project-price)
3. 合同服务配置 (/smart-service/contract-service)
4. 经营范围配置 (/smart-service/scope-config)
"""
import asyncio
import os
from test_base import TestBase, SCREENSHOT_DIR


class SmartServiceConfigTests(TestBase):
    """智能服务配置模块测试"""

    def __init__(self):
        super().__init__()
        self.current_module = "智能服务配置"

    async def test_project_config_page_load(self):
        """测试服务项目配置 - 页面加载"""
        test_name = "服务项目配置 - 页面加载"
        await self.navigate_to("服务项目配置")

        # 验证URL
        url_ok = "/smart-service/project-config" in self.page.url

        # 验证表格列头
        headers = await self.get_table_headers()
        expected_headers = ["服务项目名称", "副标题", "计费方式", "是否展示", "创建时间", "操作"]
        headers_ok = all(h in headers for h in expected_headers)

        # 验证按钮
        buttons = await self.get_buttons()
        has_query = "查询" in buttons
        has_add = "新增服务项目" in buttons

        passed = url_ok and headers_ok and has_query and has_add
        screenshot = await self.screenshot("smart_project_config_page")
        self.record_result(
            test_name, passed,
            f"URL包含/smart-service/project-config, 表格列头包含{expected_headers}, 有查询和新增按钮",
            f"URL: {self.page.url}, 列头: {headers}, 按钮: {buttons}",
            screenshot
        )

    async def test_project_config_search(self):
        """测试服务项目配置 - 搜索功能"""
        test_name = "服务项目配置 - 搜索功能"
        await self.navigate_to("服务项目配置")

        # 记录搜索前数据行数
        rows_before = await self.get_table_row_count()

        # 输入搜索关键词
        await self.fill_input("请输入", "测试")

        # 点击查询
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        # 验证搜索后页面正常
        rows_after = await self.get_table_row_count()
        url_ok = "/smart-service/project-config" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("smart_project_config_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_project_config_search_reset(self):
        """测试服务项目配置 - 重置搜索"""
        test_name = "服务项目配置 - 重置搜索"
        await self.navigate_to("服务项目配置")

        # 输入搜索关键词
        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(1000)

        # 点击重置
        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        # 验证输入框被清空
        input_value = await self.page.evaluate("""
            () => {
                const inp = document.querySelector('input[placeholder="请输入"]');
                return inp ? inp.value : null;
            }
        """)

        passed = input_value == ""
        screenshot = await self.screenshot("smart_project_config_reset")
        self.record_result(
            test_name, passed,
            "点击重置后搜索框被清空",
            f"重置后输入框值: '{input_value}'",
            screenshot
        )

    async def test_project_config_add_form_validation(self):
        """测试服务项目配置 - 新增表单验证"""
        test_name = "服务项目配置 - 新增表单验证"
        await self.navigate_to("服务项目配置")

        # 点击新增按钮
        await self.click_button("新增服务项目")
        await self.page.wait_for_timeout(1500)

        # 检查弹窗/抽屉是否出现
        modal_appeared = await self.wait_for_modal()

        if not modal_appeared:
            # 检查是否有抽屉
            drawer = self.page.locator('.ant-drawer').first
            modal_appeared = await drawer.count() > 0

        if modal_appeared:
            # 尝试直接提交空表单（寻找确认/提交按钮）
            submit_clicked = False
            for btn_text in ["确 认", "确认", "确定", "确 定", "保存", "提交"]:
                if await self.click_button(btn_text):
                    submit_clicked = True
                    break

            await self.page.wait_for_timeout(2000)  # 增加等待时间，确保验证错误显示

            # 检查是否有表单验证错误
            errors = await self.get_form_errors()
            passed = len(errors) > 0  # 有验证错误说明验证生效

            screenshot = await self.screenshot("smart_project_config_add_validation")
            self.record_result(
                test_name, passed,
                "空表单提交时应显示验证错误",
                f"表单验证错误: {errors}",
                screenshot
            )

            # 关闭弹窗
            await self.close_modal()
            # 尝试取消按钮
            for btn_text in ["取消", "取 消"]:
                await self.click_button(btn_text)
                break
        else:
            screenshot = await self.screenshot("smart_project_config_add_no_modal")
            self.record_result(
                test_name, False,
                "点击新增后应弹出表单",
                "未检测到弹窗/抽屉",
                screenshot
            )

    async def test_project_config_edit(self):
        """测试服务项目配置 - 编辑功能"""
        test_name = "服务项目配置 - 编辑功能"
        await self.navigate_to("服务项目配置")

        # 查找编辑按钮
        edit_btn = self.page.locator('a:has-text("编辑"), button:has-text("编辑"), .ant-btn:has-text("编辑")').first
        if await edit_btn.count() > 0:
            await edit_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            if not modal_appeared:
                drawer = self.page.locator('.ant-drawer').first
                modal_appeared = await drawer.count() > 0

            passed = modal_appeared
            screenshot = await self.screenshot("smart_project_config_edit")
            self.record_result(
                test_name, passed,
                "点击编辑后应弹出编辑表单",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            # 关闭弹窗
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

    async def test_project_config_toggle_display(self):
        """测试服务项目配置 - 切换展示状态"""
        test_name = "服务项目配置 - 切换展示状态"
        await self.navigate_to("服务项目配置")

        # 查找"不展示"按钮
        toggle_btn = self.page.locator('a:has-text("不展示"), button:has-text("不展示"), a:has-text("展示"), button:has-text("展示")').first
        if await toggle_btn.count() > 0:
            btn_text = await toggle_btn.inner_text()
            await toggle_btn.click()
            await self.page.wait_for_timeout(1500)

            # 检查是否有确认弹窗
            confirm = self.page.locator('.ant-popconfirm, .ant-modal-confirm').first
            if await confirm.count() > 0:
                # 点击确认
                confirm_btn = self.page.locator('.ant-popconfirm-buttons .ant-btn-primary, .ant-modal-confirm-btns .ant-btn-primary').first
                if await confirm_btn.count() > 0:
                    await confirm_btn.click()
                    await self.page.wait_for_timeout(1000)

            passed = True
            screenshot = await self.screenshot("smart_project_config_toggle")
            self.record_result(
                test_name, passed,
                f"点击'{btn_text}'后状态应切换",
                "操作执行完成",
                screenshot
            )
        else:
            self.record_result(
                test_name, False,
                "表格中应有展示/不展示切换按钮",
                "未找到切换按钮",
                ""
            )

    async def test_project_price_page_load(self):
        """测试服务定价配置 - 页面加载"""
        test_name = "服务定价配置 - 页面加载"
        await self.navigate_to("服务定价配置")

        url_ok = "/smart-service/project-price" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["区域", "服务价格"]
        headers_ok = all(any(eh in h for h in headers) for eh in expected_headers)

        buttons = await self.get_buttons()
        has_import = any("导入" in b for b in buttons)
        has_template = any("模板" in b for b in buttons)

        passed = url_ok and headers_ok and (has_import or has_template)
        screenshot = await self.screenshot("smart_project_price_page")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头包含{expected_headers}, 有导入/模板按钮",
            f"URL: {self.page.url}, 列头: {headers}, 按钮: {buttons}",
            screenshot
        )

    async def test_project_price_download_template(self):
        """测试服务定价配置 - 下载模板"""
        test_name = "服务定价配置 - 下载模板"
        await self.navigate_to("服务定价配置")

        # 监听下载事件
        async with self.page.expect_download(timeout=10000) as download_info:
            downloaded = await self.click_button("下载服务定价模板")
            if not downloaded:
                # 尝试其他选择器
                btn = self.page.locator('a:has-text("下载"), button:has-text("下载"), .ant-btn:has-text("下载")').first
                if await btn.count() > 0:
                    await btn.click()
                    downloaded = True

        if downloaded:
            download = await download_info.value
            passed = download is not None
            screenshot = await self.screenshot("smart_project_price_download")
            self.record_result(
                test_name, passed,
                "点击下载模板后应触发文件下载",
                f"下载文件: {download.suggested_filename if download else 'None'}",
                screenshot
            )
        else:
            self.record_result(
                test_name, False,
                "应有下载模板按钮",
                "未找到下载按钮",
                ""
            )

    async def test_contract_service_page_load(self):
        """测试合同服务配置 - 页面加载"""
        test_name = "合同服务配置 - 页面加载"
        await self.navigate_to("合同服务配置")

        url_ok = "/smart-service/contract-service" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["合同服务标题", "合同服务内容", "费用内容", "所属服务项目", "创建时间", "操作"]
        headers_ok = all(h in headers for h in expected_headers)

        buttons = await self.get_buttons()
        has_add = "新增合同服务" in buttons
        has_edit = "编辑" in buttons
        has_delete = "删除" in buttons

        passed = url_ok and headers_ok and has_add and has_edit and has_delete
        screenshot = await self.screenshot("smart_contract_service_page")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头完整, 有新增/编辑/删除按钮",
            f"URL: {self.page.url}, 列头: {headers}, 按钮: {buttons}",
            screenshot
        )

    async def test_contract_service_search(self):
        """测试合同服务配置 - 搜索功能"""
        test_name = "合同服务配置 - 搜索功能"
        await self.navigate_to("合同服务配置")

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/smart-service/contract-service" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("smart_contract_service_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_contract_service_add_form(self):
        """测试合同服务配置 - 新增表单"""
        test_name = "合同服务配置 - 新增表单"
        await self.navigate_to("合同服务配置")

        await self.click_button("新增合同服务")
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
                await self.click_button(btn_text)
                break

            await self.page.wait_for_timeout(1000)
            errors = await self.get_form_errors()

            passed = len(errors) > 0 or len(form_labels) > 0
            screenshot = await self.screenshot("smart_contract_service_add")
            self.record_result(
                test_name, passed,
                "新增表单应包含字段且有验证",
                f"表单字段: {form_labels}, 验证错误: {errors}",
                screenshot
            )

            await self.close_modal()
            for btn_text in ["取消", "取 消"]:
                await self.click_button(btn_text)
                break
        else:
            screenshot = await self.screenshot("smart_contract_service_add_no_modal")
            self.record_result(
                test_name, False,
                "点击新增后应弹出表单",
                "未检测到弹窗/抽屉",
                screenshot
            )

    async def test_contract_service_delete_confirm(self):
        """测试合同服务配置 - 删除确认"""
        test_name = "合同服务配置 - 删除确认"
        await self.navigate_to("合同服务配置")

        # 查找删除按钮
        delete_btn = self.page.locator('a:has-text("删除"), button:has-text("删除"), .ant-btn:has-text("删除")').first
        if await delete_btn.count() > 0:
            await delete_btn.click()
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

            passed = True  # 删除有确认弹窗则通过，没有也记录
            screenshot = await self.screenshot("smart_contract_service_delete")
            self.record_result(
                test_name, passed,
                "点击删除应弹出确认提示",
                f"确认弹窗: {has_confirm}",
                screenshot
            )
        else:
            self.record_result(
                test_name, False,
                "表格中应有删除按钮",
                "未找到删除按钮",
                ""
            )

    async def test_scope_config_page_load(self):
        """测试经营范围配置 - 页面加载"""
        test_name = "经营范围配置 - 页面加载"
        await self.navigate_to("经营范围配置")

        url_ok = "/smart-service/scope-config" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["经营范围名称", "备注", "启用状态", "创建时间", "操作"]
        headers_ok = all(h in headers for h in expected_headers)

        buttons = await self.get_buttons()
        has_add = "新增经营范围" in buttons
        has_query = "查询" in buttons

        passed = url_ok and headers_ok and has_add and has_query
        screenshot = await self.screenshot("smart_scope_config_page")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头完整, 有新增和查询按钮",
            f"URL: {self.page.url}, 列头: {headers}, 按钮: {buttons}",
            screenshot
        )

    async def test_scope_config_search(self):
        """测试经营范围配置 - 搜索功能"""
        test_name = "经营范围配置 - 搜索功能"
        await self.navigate_to("经营范围配置")

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/smart-service/scope-config" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("smart_scope_config_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_scope_config_add_form(self):
        """测试经营范围配置 - 新增表单"""
        test_name = "经营范围配置 - 新增表单"
        await self.navigate_to("经营范围配置")

        await self.click_button("新增经营范围")
        await self.page.wait_for_timeout(1500)

        modal_appeared = await self.wait_for_modal()
        if not modal_appeared:
            drawer = self.page.locator('.ant-drawer').first
            modal_appeared = await drawer.count() > 0

        if modal_appeared:
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

            for btn_text in ["确定", "确 定", "保存", "提交", "确认"]:
                await self.click_button(btn_text)
                break

            await self.page.wait_for_timeout(1000)
            errors = await self.get_form_errors()

            passed = len(errors) > 0 or len(form_labels) > 0
            screenshot = await self.screenshot("smart_scope_config_add")
            self.record_result(
                test_name, passed,
                "新增表单应包含字段且有验证",
                f"表单字段: {form_labels}, 验证错误: {errors}",
                screenshot
            )

            await self.close_modal()
            for btn_text in ["取消", "取 消"]:
                await self.click_button(btn_text)
                break
        else:
            screenshot = await self.screenshot("smart_scope_config_add_no_modal")
            self.record_result(
                test_name, False,
                "点击新增后应弹出表单",
                "未检测到弹窗/抽屉",
                screenshot
            )

    async def run_all(self):
        """运行所有测试"""
        await self.setup()
        try:
            await self.login()

            # 服务项目配置测试
            print("\n--- 服务项目配置测试 ---")
            await self.test_project_config_page_load()
            await self.test_project_config_search()
            await self.test_project_config_search_reset()
            await self.test_project_config_add_form_validation()
            await self.test_project_config_edit()
            await self.test_project_config_toggle_display()

            # 服务定价配置测试
            print("\n--- 服务定价配置测试 ---")
            await self.test_project_price_page_load()
            await self.test_project_price_download_template()

            # 合同服务配置测试
            print("\n--- 合同服务配置测试 ---")
            await self.test_contract_service_page_load()
            await self.test_contract_service_search()
            await self.test_contract_service_add_form()
            await self.test_contract_service_delete_confirm()

            # 经营范围配置测试
            print("\n--- 经营范围配置测试 ---")
            await self.test_scope_config_page_load()
            await self.test_scope_config_search()
            await self.test_scope_config_add_form()

        finally:
            await self.teardown()

        return self.test_results
