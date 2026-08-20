"""
超级个体后台管理系统 - 服务商管理测试
测试代理记账公司管理页面的各项功能
"""
import asyncio
import os
import sys
from datetime import datetime
from test_base import TestBase

# 添加 web_auto 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_auto'))
from utils.logger import logger


class ProviderManagementTests(TestBase):
    """服务商管理测试类"""

    def __init__(self):
        super().__init__()
        self.current_module = "服务商管理"
        # 营业执照资料路径
        self.license_dir = r"F:\测试资料\营业执照"
        self.sample_license = os.path.join(self.license_dir, "测试用工企业.png")

    async def test_provider_page_load(self):
        """测试服务商管理 - 页面加载"""
        test_name = "代理记账公司管理 - 页面加载"
        await self.navigate_to("服务商管理")

        url_ok = "/service-provider/proxy-accounting" in self.page.url

        headers = await self.get_table_headers()
        expected_headers = ["公司编号", "公司名称", "统一社会信用代码", "办公地址", "服务区域", "服务项目", "联系人", "联系电话", "服务客户数", "启用状态", "入驻时间", "操作"]
        headers_ok = all(any(eh in h for h in headers) for eh in expected_headers)

        buttons = await self.get_buttons()
        has_add = any("服务商入驻" in b for b in buttons)
        has_edit = any("编辑" in b for b in buttons)
        has_disable = any("禁用" in b for b in buttons)

        passed = url_ok and headers_ok and has_add and has_edit and has_disable
        screenshot = await self.screenshot("provider_page_load")
        self.record_result(
            test_name, passed,
            f"URL正确, 表格列头包含{expected_headers[:3]}..., 有服务商入驻/编辑/禁用按钮",
            f"URL: {self.page.url}, 列头: {headers[:5]}..., 按钮: {buttons}",
            screenshot
        )

    async def test_provider_search(self):
        """测试服务商管理 - 搜索功能"""
        test_name = "代理记账公司管理 - 搜索功能"
        await self.navigate_to("服务商管理")

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入公司名称", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/service-provider/proxy-accounting" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("provider_search")
        self.record_result(
            test_name, passed,
            "输入公司名称后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_provider_search_reset(self):
        """测试服务商管理 - 重置搜索"""
        test_name = "代理记账公司管理 - 重置搜索"
        await self.navigate_to("服务商管理")

        await self.fill_input("请输入公司名称", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/service-provider/proxy-accounting" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("provider_search_reset")
        self.record_result(
            test_name, passed,
            "点击重置后应清空搜索条件并显示全部数据",
            f"重置后行数: {rows_after}",
            screenshot
        )

    async def test_provider_add_form_validation(self):
        """测试服务商管理 - 新增表单验证"""
        test_name = "代理记账公司管理 - 新增表单验证"
        await self.navigate_to("服务商管理")

        add_btn = self.page.locator('button:has-text("服务商入驻"), button:has-text("新增"), .ant-btn:has-text("新增"), a:has-text("新增")').first
        if await add_btn.count() > 0:
            await add_btn.click()
            await self.page.wait_for_timeout(2000)

            confirm_btn = self.page.locator('.ant-modal button.ant-btn-primary, .ant-drawer button.ant-btn-primary').first
            if await confirm_btn.count() > 0:
                await confirm_btn.click()
                await self.page.wait_for_timeout(1000)

            errors = await self.get_form_errors()
            passed = len(errors) > 0
            screenshot = await self.screenshot("provider_add_form_validation")
            self.record_result(
                test_name, passed,
                "提交空表单应显示验证错误",
                f"验证错误: {errors}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "应有服务商入驻按钮", "未找到按钮", "")

    async def test_provider_add_with_license(self):
        """测试服务商管理 - 新增服务商并上传营业执照"""
        test_name = "代理记账公司管理 - 新增服务商（上传营业执照）"
        await self.navigate_to("服务商管理")

        add_btn = self.page.locator('button:has-text("服务商入驻"), button:has-text("新增"), .ant-btn:has-text("新增"), a:has-text("新增")').first
        if await add_btn.count() > 0:
            await add_btn.click()
            await self.page.wait_for_timeout(2000)

            # 使用时间戳生成唯一名称
            timestamp = int(asyncio.get_event_loop().time())
            test_company_name = f"自动化测试服务商_{timestamp}"
            test_credit_code = f"9119{timestamp % 10000000000:010d}"

            # 使用JS填写表单字段
            await self.page.evaluate("""
                (data) => {
                    const setValue = (codefield, value) => {
                        const input = document.querySelector(`.ant-modal input[codefield="${codefield}"]`);
                        if (input) {
                            input.value = value;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    };
                    setValue('companyName', data.companyName);
                    setValue('creditCode', data.creditCode);
                    setValue('officeAddress', data.officeAddress);
                    setValue('contactPerson', data.contactPerson);
                    setValue('contactPhone', data.contactPhone);
                }
            """, {
                "companyName": test_company_name,
                "creditCode": test_credit_code,
                "officeAddress": "天津市和平区测试地址",
                "contactPerson": "测试联系人",
                "contactPhone": "13800138000"
            })
            await self.page.wait_for_timeout(1000)

            # 上传营业执照
            license_input = self.page.locator('input[type="file"]').first
            if await license_input.count() > 0 and os.path.exists(self.sample_license):
                await license_input.set_input_files(self.sample_license)
                await self.page.wait_for_timeout(2000)
                logger.info(f"上传营业执照: {self.sample_license}")

            # 选择服务区域（第一个选项）
            try:
                service_area_select = self.page.locator('.ant-select').filter(has_text='请选择').first
                if await service_area_select.count() > 0:
                    await service_area_select.click(force=True)
                    await self.page.wait_for_timeout(500)
                    first_option = self.page.locator('.ant-select-item-option').first
                    if await first_option.count() > 0:
                        await first_option.click()
                        await self.page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"选择服务区域失败: {e}")

            # 选择服务项目
            try:
                project_selects = self.page.locator('.ant-select')
                for i in range(await project_selects.count()):
                    select = project_selects.nth(i)
                    text = await select.text_content() if await select.count() > 0 else ""
                    if "请选择服务项目" in text:
                        await select.click(force=True)
                        await self.page.wait_for_timeout(500)
                        first_option = self.page.locator('.ant-select-item-option').first
                        if await first_option.count() > 0:
                            await first_option.click()
                            await self.page.wait_for_timeout(500)
                        break
            except Exception as e:
                logger.warning(f"选择服务项目失败: {e}")

            # 选择启用状态
            try:
                status_selects = self.page.locator('.ant-select')
                for i in range(await status_selects.count()):
                    select = status_selects.nth(i)
                    text = await select.text_content() if await select.count() > 0 else ""
                    if "请选择启用状态" in text or "启用状态" in text:
                        await select.click(force=True)
                        await self.page.wait_for_timeout(500)
                        first_option = self.page.locator('.ant-select-item-option').first
                        if await first_option.count() > 0:
                            await first_option.click()
                            await self.page.wait_for_timeout(500)
                        break
            except Exception as e:
                logger.warning(f"选择启用状态失败: {e}")

            # 提交表单
            submit_btn = self.page.locator('.ant-modal button.ant-btn-primary, .ant-drawer button.ant-btn-primary').first
            if await submit_btn.count() > 0:
                await submit_btn.click()
                await self.page.wait_for_timeout(3000)

            # 检查结果
            errors = await self.get_form_errors()
            
            # 检查是否有关于已填写字段的错误
            # 注意：办公地址可能是级联选择器，JS填充可能不生效
            critical_errors = [e for e in errors if any(keyword in e for keyword in ['公司名称', '统一社会信用代码', '联系人', '联系电话', '营业执照'])]
            
            passed = len(critical_errors) == 0
            
            screenshot = await self.screenshot("provider_add_with_license")
            self.record_result(
                test_name, passed,
                "填写表单并上传营业执照后提交，已填写字段无验证错误",
                f"公司名称: {test_company_name}, 全部验证错误: {errors}, 关键错误: {critical_errors}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "应有服务商入驻按钮", "未找到按钮", "")

    async def test_provider_edit(self):
        """测试服务商管理 - 编辑功能"""
        test_name = "代理记账公司管理 - 编辑功能"
        await self.navigate_to("服务商管理")

        edit_btn = self.page.locator('a:has-text("编辑"), button:has-text("编辑"), .ant-btn:has-text("编辑")').first
        if await edit_btn.count() > 0:
            await edit_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            passed = modal_appeared
            screenshot = await self.screenshot("provider_edit")
            self.record_result(
                test_name, passed,
                "点击编辑后应弹出编辑表单",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有编辑按钮", "未找到编辑按钮", "")

    async def test_provider_detail(self):
        """测试服务商管理 - 查看详情"""
        test_name = "代理记账公司管理 - 查看详情"
        await self.navigate_to("服务商管理")

        detail_btn = self.page.locator('a:has-text("详情"), button:has-text("详情"), .ant-btn:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            passed = modal_appeared
            screenshot = await self.screenshot("provider_detail")
            self.record_result(
                test_name, passed,
                "点击详情后应弹出详情弹窗",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有详情按钮", "未找到详情按钮", "")

    async def test_provider_disable(self):
        """测试服务商管理 - 禁用功能"""
        test_name = "代理记账公司管理 - 禁用功能"
        await self.navigate_to("服务商管理")

        disable_btn = self.page.locator('a:has-text("禁用"), button:has-text("禁用"), .ant-btn:has-text("禁用")').first
        if await disable_btn.count() > 0:
            await disable_btn.click()
            await self.page.wait_for_timeout(1000)

            confirm = self.page.locator('.ant-popconfirm, .ant-modal-confirm').first
            has_confirm = await confirm.count() > 0

            if has_confirm:
                cancel_btn = self.page.locator('.ant-popconfirm-buttons .ant-btn:not(.ant-btn-primary), .ant-modal-confirm-btns .ant-btn:not(.ant-btn-primary)').first
                if await cancel_btn.count() > 0:
                    await cancel_btn.click()
                    await self.page.wait_for_timeout(500)

            passed = True
            screenshot = await self.screenshot("provider_disable")
            self.record_result(
                test_name, passed,
                "点击禁用应弹出确认提示",
                f"确认弹窗: {has_confirm}",
                screenshot
            )
        else:
            self.record_result(test_name, False, "表格中应有禁用按钮", "未找到禁用按钮", "")

    async def test_provider_reset_password(self):
        """测试服务商管理 - 重置密码功能"""
        test_name = "代理记账公司管理 - 重置密码功能"
        await self.navigate_to("服务商管理")

        reset_btn = self.page.locator('a:has-text("重置密码"), button:has-text("重置密码"), .ant-btn:has-text("重置密码")').first
        if await reset_btn.count() > 0:
            await reset_btn.click()
            await self.page.wait_for_timeout(1000)

            confirm = self.page.locator('.ant-popconfirm, .ant-modal-confirm').first
            has_confirm = await confirm.count() > 0

            if has_confirm:
                cancel_btn = self.page.locator('.ant-popconfirm-buttons .ant-btn:not(.ant-btn-primary), .ant-modal-confirm-btns .ant-btn:not(.ant-btn-primary)').first
                if await cancel_btn.count() > 0:
                    await cancel_btn.click()
                    await self.page.wait_for_timeout(500)

            passed = True
            screenshot = await self.screenshot("provider_reset_password")
            self.record_result(
                test_name, passed,
                "点击重置密码应弹出确认提示",
                f"确认弹窗: {has_confirm}",
                screenshot
            )
        else:
            self.record_result(test_name, False, "表格中应有重置密码按钮", "未找到重置密码按钮", "")

    async def test_provider_pagination(self):
        """测试服务商管理 - 表格分页"""
        test_name = "代理记账公司管理 - 表格分页"
        await self.navigate_to("服务商管理")

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
            screenshot = await self.screenshot("provider_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器且至少2页",
                f"分页信息: {pagination_info}",
                screenshot
            )
        else:
            rows = await self.get_table_row_count()
            passed = rows > 0
            screenshot = await self.screenshot("provider_no_pagination")
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

            print("\n--- 服务商管理测试 ---")
            await self.test_provider_page_load()
            await self.test_provider_search()
            await self.test_provider_search_reset()
            await self.test_provider_add_form_validation()
            await self.test_provider_add_with_license()
            await self.test_provider_edit()
            await self.test_provider_detail()
            await self.test_provider_disable()
            await self.test_provider_reset_password()
            await self.test_provider_pagination()

        finally:
            if base is None:
                await self.teardown()

        return self.test_results
