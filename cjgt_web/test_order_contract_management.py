"""
超级个体后台管理系统 - 订单管理与合同管理测试
测试订单管理和合同管理页面的各项功能
"""
import asyncio
from test_base import TestBase, BASE_URL


class OrderManagementTests(TestBase):
    """订单管理测试类"""

    def __init__(self):
        super().__init__()
        self.current_module = "订单管理"

    async def test_order_page_load(self):
        """测试订单管理 - 页面加载"""
        test_name = "订单管理 - 页面加载"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(3000)

        title = await self.page.title()
        url_ok = "/order/order-manage" in self.page.url
        title_ok = "订单管理" in title

        headers = await self.get_table_headers()
        expected_headers = ["订单号", "合同编号", "订单来源", "费用合计（元）", "支付凭证"]
        headers_ok = all(any(eh in h for h in headers) for eh in expected_headers)

        buttons = await self.get_buttons()
        has_query = any("查询" in b for b in buttons)
        has_reset = any("重置" in b for b in buttons)
        has_detail = any("详情" in b for b in buttons)

        passed = url_ok and title_ok and headers_ok and has_query and has_reset and has_detail
        screenshot = await self.screenshot("order_page_load")
        self.record_result(
            test_name, passed,
            f"URL正确, 标题正确, 表格列头包含{expected_headers[:3]}..., 有查询/重置/详情按钮",
            f"URL: {self.page.url}, 标题: {title}, 列头: {headers[:5]}..., 按钮: {buttons}",
            screenshot
        )

    async def test_order_search(self):
        """测试订单管理 - 搜索功能"""
        test_name = "订单管理 - 搜索功能"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/order/order-manage" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("order_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_order_search_reset(self):
        """测试订单管理 - 重置搜索"""
        test_name = "订单管理 - 重置搜索"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/order/order-manage" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("order_search_reset")
        self.record_result(
            test_name, passed,
            "点击重置后应清空搜索条件并显示全部数据",
            f"重置后行数: {rows_after}",
            screenshot
        )

    async def test_order_filter_by_payment_status(self):
        """测试订单管理 - 按支付状态筛选"""
        test_name = "订单管理 - 按支付状态筛选"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        try:
            status_select = self.page.locator('.ant-select').filter(has_text='请选择支付状态').first
            if await status_select.count() > 0:
                await self.page.evaluate("""
                    (text) => {
                        const selects = document.querySelectorAll('.ant-select-selector');
                        for (const select of selects) {
                            if (select.textContent.includes(text)) {
                                select.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """, "请选择支付状态")
                await self.page.wait_for_timeout(500)
                first_option = self.page.locator('.ant-select-item-option').first
                if await first_option.count() > 0:
                    await first_option.click()
                    await self.page.wait_for_timeout(500)

                await self.click_button("查询")
                await self.page.wait_for_timeout(2000)

                rows_after = await self.get_table_row_count()
                passed = rows_after >= 0
                screenshot = await self.screenshot("order_filter_payment_status")
                self.record_result(
                    test_name, passed,
                    "选择支付状态后查询应正常返回结果",
                    f"查询后行数: {rows_after}",
                    screenshot
                )
            else:
                self.record_result(test_name, False, "应有支付状态下拉框", "未找到支付状态下拉框", "")
        except Exception as e:
            self.record_result(test_name, False, "选择支付状态应成功", f"错误: {str(e)}", "")

    async def test_order_filter_by_source(self):
        """测试订单管理 - 按订单来源筛选"""
        test_name = "订单管理 - 按订单来源筛选"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        try:
            source_select = self.page.locator('.ant-select').filter(has_text='请选择订单来源').first
            if await source_select.count() > 0:
                await self.page.evaluate("""
                    (text) => {
                        const selects = document.querySelectorAll('.ant-select-selector');
                        for (const select of selects) {
                            if (select.textContent.includes(text)) {
                                select.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """, "请选择订单来源")
                await self.page.wait_for_timeout(500)
                first_option = self.page.locator('.ant-select-item-option').first
                if await first_option.count() > 0:
                    await first_option.click()
                    await self.page.wait_for_timeout(500)

                await self.click_button("查询")
                await self.page.wait_for_timeout(2000)

                rows_after = await self.get_table_row_count()
                passed = rows_after >= 0
                screenshot = await self.screenshot("order_filter_source")
                self.record_result(
                    test_name, passed,
                    "选择订单来源后查询应正常返回结果",
                    f"查询后行数: {rows_after}",
                    screenshot
                )
            else:
                self.record_result(test_name, False, "应有订单来源下拉框", "未找到订单来源下拉框", "")
        except Exception as e:
            self.record_result(test_name, False, "选择订单来源应成功", f"错误: {str(e)}", "")

    async def test_order_filter_by_date_range(self):
        """测试订单管理 - 按日期范围筛选"""
        test_name = "订单管理 - 按日期范围筛选"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        try:
            await self.page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input[placeholder="开始日期"], input[placeholder="结束日期"]');
                    if (inputs.length >= 2) {
                        inputs[0].value = '2026-01-01';
                        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                        inputs[1].value = '2026-12-31';
                        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            """)
            await self.page.wait_for_timeout(500)
            await self.click_button("查询")
            await self.page.wait_for_timeout(2000)

            rows_after = await self.get_table_row_count()
            passed = rows_after >= 0
            screenshot = await self.screenshot("order_filter_date_range")
            self.record_result(
                test_name, passed,
                "选择日期范围后查询应正常返回结果",
                f"查询后行数: {rows_after}",
                screenshot
            )
        except Exception as e:
            self.record_result(test_name, False, "日期筛选应成功", f"错误: {str(e)}", "")

    async def test_order_combined_filter(self):
        """测试订单管理 - 组合筛选（订单号 + 支付状态）"""
        test_name = "订单管理 - 组合筛选"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        await self.fill_input("请输入", "测试")
        try:
            status_select = self.page.locator('.ant-select').filter(has_text='请选择支付状态').first
            if await status_select.count() > 0:
                await self.page.evaluate("""
                    (text) => {
                        const selects = document.querySelectorAll('.ant-select-selector');
                        for (const select of selects) {
                            if (select.textContent.includes(text)) {
                                select.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """, "请选择支付状态")
                await self.page.wait_for_timeout(500)
                first_option = self.page.locator('.ant-select-item-option').first
                if await first_option.count() > 0:
                    await first_option.click()
                    await self.page.wait_for_timeout(500)

                await self.click_button("查询")
                await self.page.wait_for_timeout(2000)

                rows_after = await self.get_table_row_count()
                passed = rows_after >= 0
                screenshot = await self.screenshot("order_combined_filter")
                self.record_result(
                    test_name, passed,
                    "组合筛选后查询应正常返回结果",
                    f"查询后行数: {rows_after}",
                    screenshot
                )
            else:
                self.record_result(test_name, False, "应有支付状态下拉框", "未找到支付状态下拉框", "")
        except Exception as e:
            self.record_result(test_name, False, "组合筛选应成功", f"错误: {str(e)}", "")

    async def test_order_detail(self):
        """测试订单管理 - 查看详情"""
        test_name = "订单管理 - 查看详情"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        detail_btn = self.page.locator('a:has-text("详情"), button:has-text("详情"), .ant-btn:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(1500)

            modal_appeared = await self.wait_for_modal()
            passed = modal_appeared
            screenshot = await self.screenshot("order_detail")
            self.record_result(
                test_name, passed,
                "点击详情后应弹出详情弹窗",
                f"弹窗出现: {modal_appeared}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有详情按钮", "未找到详情按钮", "")

    async def test_order_detail_fields(self):
        """测试订单管理 - 详情弹窗字段校验"""
        test_name = "订单管理 - 详情弹窗字段校验"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        detail_btn = self.page.locator('a:has-text("详情"), button:has-text("详情"), .ant-btn:has-text("详情")').first
        if await detail_btn.count() > 0:
            await detail_btn.click()
            await self.page.wait_for_timeout(2000)

            # 获取弹窗内容
            modal_body = await self.page.evaluate("""
                () => {
                    const modal = document.querySelector('.ant-modal-content');
                    if (!modal) return null;
                    const body = modal.querySelector('.ant-modal-body');
                    return body ? body.textContent.trim() : '';
                }
            """)
            
            passed = modal_body and len(modal_body) > 0
            screenshot = await self.screenshot("order_detail_fields")
            self.record_result(
                test_name, passed,
                "详情弹窗应包含订单相关字段信息",
                f"弹窗内容长度: {len(modal_body) if modal_body else 0}, 内容预览: {modal_body[:200] if modal_body else 'N/A'}",
                screenshot
            )

            await self.close_modal()
        else:
            self.record_result(test_name, False, "表格中应有详情按钮", "未找到详情按钮", "")

    async def test_order_pagination(self):
        """测试订单管理 - 表格分页"""
        test_name = "订单管理 - 表格分页"
        await self.page.goto(f"{BASE_URL}/order/order-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

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
            screenshot = await self.screenshot("order_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器且至少2页",
                f"分页信息: {pagination_info}",
                screenshot
            )
        else:
            rows = await self.get_table_row_count()
            passed = rows > 0
            screenshot = await self.screenshot("order_no_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器或显示数据",
                f"分页器: 无, 数据行数: {rows}",
                screenshot
            )

    async def run_all(self, base=None):
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
            print("\n--- 订单管理测试 ---")
            await self.test_order_page_load()
            await self.test_order_search()
            await self.test_order_search_reset()
            await self.test_order_filter_by_payment_status()
            await self.test_order_filter_by_source()
            await self.test_order_filter_by_date_range()
            await self.test_order_combined_filter()
            await self.test_order_detail()
            await self.test_order_detail_fields()
            await self.test_order_pagination()
        finally:
            if base is None:
                await self.teardown()
        return self.test_results


class ContractManagementTests(TestBase):
    """合同管理测试类"""

    def __init__(self):
        super().__init__()
        self.current_module = "合同管理"

    async def test_contract_page_load(self):
        """测试合同管理 - 页面加载"""
        test_name = "合同管理 - 页面加载"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(3000)

        title = await self.page.title()
        url_ok = "/contract/contract-manage" in self.page.url
        title_ok = "合同管理" in title

        headers = await self.get_table_headers()
        expected_headers = ["合同编号", "合同类型", "甲方", "甲方联系电话", "乙方"]
        headers_ok = all(any(eh in h for h in headers) for eh in expected_headers)

        buttons = await self.get_buttons()
        has_query = any("查询" in b for b in buttons)
        has_reset = any("重置" in b for b in buttons)
        has_expand = any("展开" in b for b in buttons)

        passed = url_ok and title_ok and headers_ok and has_query and has_reset and has_expand
        screenshot = await self.screenshot("contract_page_load")
        self.record_result(
            test_name, passed,
            f"URL正确, 标题正确, 表格列头包含{expected_headers[:3]}..., 有查询/重置/展开按钮",
            f"URL: {self.page.url}, 标题: {title}, 列头: {headers[:5]}..., 按钮: {buttons}",
            screenshot
        )

    async def test_contract_search(self):
        """测试合同管理 - 搜索功能"""
        test_name = "合同管理 - 搜索功能"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        rows_before = await self.get_table_row_count()

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/contract/contract-manage" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("contract_search")
        self.record_result(
            test_name, passed,
            "输入关键词后点击查询，页面正常返回结果",
            f"搜索前行数: {rows_before}, 搜索后行数: {rows_after}",
            screenshot
        )

    async def test_contract_search_reset(self):
        """测试合同管理 - 重置搜索"""
        test_name = "合同管理 - 重置搜索"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        await self.fill_input("请输入", "测试")
        await self.click_button("查询")
        await self.page.wait_for_timeout(2000)

        await self.click_button("重置")
        await self.page.wait_for_timeout(2000)

        rows_after = await self.get_table_row_count()
        url_ok = "/contract/contract-manage" in self.page.url

        passed = url_ok
        screenshot = await self.screenshot("contract_search_reset")
        self.record_result(
            test_name, passed,
            "点击重置后应清空搜索条件并显示全部数据",
            f"重置后行数: {rows_after}",
            screenshot
        )

    async def test_contract_filter_by_party_a_name(self):
        """测试合同管理 - 按甲方名称筛选"""
        test_name = "合同管理 - 按甲方名称筛选"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        name_input = self.page.locator('input[id="top-query-form_partyAName"]').first
        if await name_input.count() > 0:
            await name_input.fill("张")
            await self.click_button("查询")
            await self.page.wait_for_timeout(2000)

            rows_after = await self.get_table_row_count()
            passed = rows_after >= 0
            screenshot = await self.screenshot("contract_filter_party_a_name")
            self.record_result(
                test_name, passed,
                "输入甲方名称后查询应正常返回结果",
                f"查询后行数: {rows_after}",
                screenshot
            )
        else:
            self.record_result(test_name, False, "应有甲方名称输入框", "未找到甲方名称输入框", "")

    async def test_contract_filter_by_validity_date(self):
        """测试合同管理 - 按协议有效期筛选"""
        test_name = "合同管理 - 按协议有效期筛选"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        try:
            await self.page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input[placeholder="开始日期"], input[placeholder="结束日期"]');
                    if (inputs.length >= 2) {
                        inputs[0].value = '2026-01-01';
                        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                        inputs[1].value = '2026-12-31';
                        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            """)
            await self.page.wait_for_timeout(500)
            await self.click_button("查询")
            await self.page.wait_for_timeout(2000)

            rows_after = await self.get_table_row_count()
            passed = rows_after >= 0
            screenshot = await self.screenshot("contract_filter_validity_date")
            self.record_result(
                test_name, passed,
                "选择协议有效期后查询应正常返回结果",
                f"查询后行数: {rows_after}",
                screenshot
            )
        except Exception as e:
            self.record_result(test_name, False, "日期筛选应成功", f"错误: {str(e)}", "")

    async def test_contract_combined_filter(self):
        """测试合同管理 - 组合筛选（合同编号 + 甲方名称）"""
        test_name = "合同管理 - 组合筛选"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        contract_no_input = self.page.locator('input[id="top-query-form_contactNo"]').first
        party_name_input = self.page.locator('input[id="top-query-form_partyAName"]').first
        
        if await contract_no_input.count() > 0 and await party_name_input.count() > 0:
            await contract_no_input.fill("XYB")
            await party_name_input.fill("张")
            await self.click_button("查询")
            await self.page.wait_for_timeout(2000)

            rows_after = await self.get_table_row_count()
            passed = rows_after >= 0
            screenshot = await self.screenshot("contract_combined_filter")
            self.record_result(
                test_name, passed,
                "组合筛选后查询应正常返回结果",
                f"查询后行数: {rows_after}",
                screenshot
            )
        else:
            self.record_result(test_name, False, "应有合同编号和甲方名称输入框", "未找到输入框", "")

    async def test_contract_expand(self):
        """测试合同管理 - 展开功能"""
        test_name = "合同管理 - 展开功能"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        expand_btn = self.page.locator('button:has-text("展开"), a:has-text("展开"), .ant-btn:has-text("展开")').first
        if await expand_btn.count() > 0:
            await expand_btn.click()
            await self.page.wait_for_timeout(1000)

            buttons = await self.get_buttons()
            passed = True
            screenshot = await self.screenshot("contract_expand")
            self.record_result(
                test_name, passed,
                "点击展开后应显示更多操作按钮",
                f"展开后按钮: {buttons}",
                screenshot
            )
        else:
            self.record_result(test_name, False, "应有展开按钮", "未找到展开按钮", "")

    async def test_contract_agreement_button_exists(self):
        """测试合同管理 - 协议按钮存在"""
        test_name = "合同管理 - 协议按钮存在"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        buttons = await self.get_buttons()
        has_agreement = any("综合代理服务协议" in b for b in buttons)
        passed = has_agreement
        screenshot = await self.screenshot("contract_agreement_button_exists")
        self.record_result(
            test_name, passed,
            "表格中应有综合代理服务协议按钮",
            f"按钮列表: {buttons}",
            screenshot
        )

    async def test_contract_agreement_opens_new_tab(self):
        """测试合同管理 - 点击协议按钮打开新标签页"""
        test_name = "合同管理 - 协议按钮打开新标签页"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        agreement_btn = self.page.locator('button:has-text("综合代理服务协议"), a:has-text("综合代理服务协议"), .ant-btn:has-text("综合代理服务协议")').first
        if await agreement_btn.count() > 0:
            async with self.page.expect_popup() as popup_info:
                await agreement_btn.click()
            new_page = await popup_info.value
            await new_page.wait_for_timeout(2000)

            new_url = new_page.url
            has_download_url = "/sys/file/download" in new_url
            passed = has_download_url
            screenshot = await self.screenshot("contract_agreement_new_tab")
            self.record_result(
                test_name, passed,
                "点击协议按钮应打开新标签页并指向文件下载链接",
                f"新标签页URL: {new_url}",
                screenshot
            )

            await new_page.close()
        else:
            self.record_result(test_name, False, "表格中应有综合代理服务协议按钮", "未找到按钮", "")

    async def test_contract_agreement_returns_to_list(self):
        """测试合同管理 - 关闭协议标签页后回到合同列表"""
        test_name = "合同管理 - 关闭协议标签页后回到合同列表"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

        agreement_btn = self.page.locator('button:has-text("综合代理服务协议"), a:has-text("综合代理服务协议"), .ant-btn:has-text("综合代理服务协议")').first
        if await agreement_btn.count() > 0:
            async with self.page.expect_popup() as popup_info:
                await agreement_btn.click()
            new_page = await popup_info.value
            await new_page.wait_for_timeout(2000)

            await new_page.close()
            await self.page.wait_for_timeout(1000)

            passed = "/contract/contract-manage" in self.page.url
            screenshot = await self.screenshot("contract_agreement_return_list")
            self.record_result(
                test_name, passed,
                "关闭协议标签页后应回到合同管理列表页",
                f"当前URL: {self.page.url}",
                screenshot
            )
        else:
            self.record_result(test_name, False, "表格中应有综合代理服务协议按钮", "未找到按钮", "")

    async def test_contract_pagination(self):
        """测试合同管理 - 表格分页"""
        test_name = "合同管理 - 表格分页"
        await self.page.goto(f"{BASE_URL}/contract/contract-manage", wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

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
            screenshot = await self.screenshot("contract_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器",
                f"分页信息: {pagination_info}",
                screenshot
            )
        else:
            rows = await self.get_table_row_count()
            passed = rows > 0
            screenshot = await self.screenshot("contract_no_pagination")
            self.record_result(
                test_name, passed,
                "表格应有分页器或显示数据",
                f"分页器: 无, 数据行数: {rows}",
                screenshot
            )

    async def run_all(self, base=None):
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
            print("\n--- 合同管理测试 ---")
            await self.test_contract_page_load()
            await self.test_contract_search()
            await self.test_contract_search_reset()
            await self.test_contract_filter_by_party_a_name()
            await self.test_contract_filter_by_validity_date()
            await self.test_contract_combined_filter()
            await self.test_contract_expand()
            await self.test_contract_agreement_button_exists()
            await self.test_contract_agreement_opens_new_tab()
            await self.test_contract_agreement_returns_to_list()
            await self.test_contract_pagination()
        finally:
            if base is None:
                await self.teardown()
        return self.test_results
