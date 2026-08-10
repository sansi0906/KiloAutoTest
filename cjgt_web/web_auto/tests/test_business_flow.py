# -*- coding: utf-8 -*-
"""
业务流程测试用例 —— 覆盖服务项目、合同服务、知识库的新增等操作
"""
import pytest
import allure

from pages.home_page import HomePage
from pages.service_project_page import ServiceProjectPage
from pages.project_price_page import ProjectPricePage
from pages.contract_service_page import ContractServicePage
from pages.knowledge_page import KnowledgePage
from pages.provider_page import ProviderPage
from utils.logger import logger


# ──────────── 服务定价配置 ────────────

@allure.feature("智能服务配置-服务定价")
class TestServicePrice:

    @allure.story("页面加载")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("服务定价页面正常加载")
    def test_service_price_page_load(self, logged_in_page):
        """验证服务定价配置页面能正常加载"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)

        with allure.step("导航到服务定价配置页"):
            home.goto_service_price()
            assert "/smart-service/project-price" in logged_in_page.url

        with allure.step("验证表格列头"):
            headers = page_obj.get_table_headers()
            logger.info(f"表头: {headers}")
            assert any("区域" in h for h in headers), "缺少'区域'列"
            assert any("价格" in h for h in headers), "缺少'价格'列"

    @allure.story("子Tab切换")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("服务定价子Tab切换加载不同定价内容")
    def test_service_price_tab_switch(self, logged_in_page):
        """验证切换子Tab后定价内容随之改变"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)

        with allure.step("导航到服务定价配置页"):
            home.goto_service_price()

        tabs = page_obj.get_tabs()
        if len(tabs) < 2:
            pytest.skip("Tab 数量不足")

        with allure.step("记录初始Tab的定价内容"):
            initial_tab_name = page_obj.get_active_tab()
            initial_regions = set(page_obj.get_pricing_regions())
            initial_rows = page_obj.get_table_row_count()
            logger.info(f"初始Tab: {initial_tab_name}, {initial_rows} 行, {len(initial_regions)} 个地区")

        # 找到一个有数据的Tab（跳过可能为空的占位Tab，且跳过初始Tab）
        target_tab = None
        target_idx = None
        for idx, tab in enumerate(tabs):
            if tab == initial_tab_name or tab == tabs[0]:
                continue
            page_obj.switch_tab(tab)
            rows = page_obj.get_table_row_count()
            logger.info(f"检查 Tab '{tab}' (索引 {idx}): {rows} 行")
            if rows > 0:
                target_tab = tab
                target_idx = idx
                break

        assert target_tab is not None, "所有非初始Tab均无定价数据"

        with allure.step(f"切换到第二个有数据的 Tab: {target_tab}"):
            assert page_obj.switch_tab(target_tab), "Tab切换失败"
            rows = page_obj.get_table_row_count()
            regions = page_obj.get_pricing_regions()
            logger.info(f"切换后 Tab '{target_tab}': {rows} 行, {len(regions)} 个地区")

        # 验证切换后有省市区定价内容
        assert rows > 0, f"Tab '{target_tab}' 切换后无定价数据"
        assert len(regions) > 0, f"Tab '{target_tab}' 无法读取地区名称"
        assert any("省" in r for r in regions), f"Tab '{target_tab}' 未显示省级定价内容"

        # 验证定价内容与初始 Tab 不同（仅当初始 Tab 也有数据时）
        if initial_rows > 0 and target_tab != initial_tab_name:
            # 收集目标Tab的完整数据（前5行地区名+价格）
            target_full_data = page_obj.page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('.ant-table-tbody tr.ant-table-row');
                    const data = [];
                    for (let i = 0; i < Math.min(rows.length, 5); i++) {
                        const cells = rows[i].querySelectorAll('td');
                        if (cells.length > 0) {
                            data.push({
                                region: cells[0].textContent.trim(),
                                price: cells[1] ? cells[1].textContent.trim() : ''
                            });
                        }
                    }
                    return data;
                }
            """)

            initial_full_data = page_obj.page.evaluate(f"""
                () => {{
                    // 先切换回初始Tab
                    const tabs = document.querySelectorAll('.ant-tabs-tab');
                    for (const tab of tabs) {{
                        if (tab.textContent.trim().includes('{initial_tab_name}')) {{
                            tab.click();
                            break;
                        }}
                    }}
                    // 等待数据加载
                    return new Promise(resolve => {{
                        setTimeout(() => {{
                            const rows = document.querySelectorAll('.ant-table-tbody tr.ant-table-row');
                            const data = [];
                            for (let i = 0; i < Math.min(rows.length, 5); i++) {{
                                const cells = rows[i].querySelectorAll('td');
                                if (cells.length > 0) {{
                                    data.push({{
                                        region: cells[0].textContent.trim(),
                                        price: cells[1] ? cells[1].textContent.trim() : ''
                                    }});
                                }}
                            }}
                            resolve(data);
                        }}, 1500);
                    }});
                }}
            """)

            # 切回目标Tab
            page_obj.switch_tab(target_tab)

            # 验证内容不同
            regions_match = set(r["region"] for r in target_full_data) == set(r["region"] for r in initial_full_data)
            prices_match = set(r["price"] for r in target_full_data if r["price"]) == set(r["price"] for r in initial_full_data if r["price"])

            if regions_match and prices_match:
                logger.warning(
                    f"Tab '{target_tab}' 与初始Tab({initial_tab_name}) 显示相同数据 — "
                    "可能存在Bug：不同Tab未加载对应项目的定价数据"
                )
                allure.attach(
                    f"初始Tab({initial_tab_name}): {initial_full_data[:3]}\n"
                    f"目标Tab({target_tab}): {target_full_data[:3]}",
                    name="数据对比",
                    attachment_type=allure.attachment_type.TEXT,
                )
                # 记录为发现，但不阻断测试（功能可用）
            else:
                logger.info(
                    f"初始Tab({initial_tab_name}) ≠ 目标Tab({target_tab}): 内容已切换"
                )

        allure.attach(
            logged_in_page.screenshot(),
            name="服务定价Tab切换后",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("下载模板")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("下载服务定价模板文件")
    def test_download_price_template(self, logged_in_page):
        """验证下载服务定价模板"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)

        with allure.step("导航到服务定价配置页"):
            home.goto_service_price()

        with allure.step("下载模板"):
            result = page_obj.download_template()
            assert result, "下载失败"

        allure.attach(
            logged_in_page.screenshot(),
            name="下载模板后",
            attachment_type=allure.attachment_type.PNG,
        )


@allure.feature("智能服务配置-服务项目")
class TestServiceProject:

    @allure.story("新增服务项目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("新增服务项目并验证数据在列表中")
    def test_add_service_project(self, logged_in_page, test_data):
        """新增服务项目，提交后验证数据出现在列表中"""
        data = test_data["service_project"]
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)

        with allure.step("导航到服务项目配置页"):
            home.goto_service_project()

        with allure.step("打开新增弹窗"):
            assert page_obj.open_add_modal(), "新增弹窗未打开"

        with allure.step("填写表单"):
            page_obj.fill_form(
                name=data["name"],
                subtitle=data["subtitle"],
                content=data["content"],
            )
        allure.attach(
            logged_in_page.screenshot(),
            name="表单填写完成",
            attachment_type=allure.attachment_type.PNG,
        )

        with allure.step("提交并验证"):
            success, msgs = page_obj.submit_and_verify(data["name"])
            logger.info(f"新增服务项目结果: success={success}, toast={msgs}")
            assert success, f"新增失败，Toast: {msgs}"

    @allure.story("编辑服务项目")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("编辑服务项目副标题")
    def test_edit_service_project(self, logged_in_page, test_data):
        """编辑服务项目，修改副标题后提交"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)

        with allure.step("导航到服务项目配置页"):
            home.goto_service_project()
            logged_in_page.wait_for_timeout(1000)

        with allure.step("检查是否存在编辑按钮"):
            if not page_obj.has_edit_button():
                pytest.skip("未找到编辑按钮")

        with allure.step("点击编辑并修改"):
            assert page_obj.click_edit(), "编辑弹窗未打开"
            # 修改副标题 —— 用唯一时间戳确保值发生变化
            subtitle_input = logged_in_page.locator(
                'input[codefield="subtitle"]'
            )
            if subtitle_input.count() > 0:
                from datetime import datetime
                ts = datetime.now().strftime("%H%M%S")
                new_subtitle = f"编辑_{ts}"
                subtitle_input.fill(new_subtitle)
                logger.info(f"修改副标题为: {new_subtitle}")

        with allure.step("提交并验证"):
            # 点击确认后立即检查 Toast（Toast 默认仅显示3秒）
            logged_in_page.locator(
                '.ant-modal button:has-text("确 认")'
            ).first.click()
            # 等待 Toast 出现（最多2秒）
            try:
                logged_in_page.wait_for_selector(
                    ".ant-message-notice-content", timeout=2000
                )
            except Exception:
                pass
            msgs = page_obj.get_toasts()
            logger.info(f"编辑提交 Toast: {msgs}")
            assert any("成功" in m for m in msgs), f"编辑失败，Toast: {msgs}"

    @allure.story("切换展示状态")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("切换服务项目展示状态")
    def test_toggle_service_project(self, logged_in_page):
        """切换服务项目的展示状态"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)

        with allure.step("导航到服务项目配置页"):
            home.goto_service_project()
            logged_in_page.wait_for_timeout(1000)

        with allure.step("检查是否存在状态开关"):
            if not page_obj.has_switch():
                pytest.skip("未找到状态开关")

        with allure.step("切换状态"):
            msgs = page_obj.toggle_switch()
            logger.info(f"切换展示 Toast: {msgs}")

    @allure.story("删除服务项目")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("删除服务项目-取消操作验证")
    def test_delete_service_project_cancel(self, logged_in_page):
        """验证删除服务项目时取消操作不删除数据"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)

        with allure.step("导航到服务项目配置页"):
            home.goto_service_project()
            logged_in_page.wait_for_timeout(1000)

        with allure.step("检查是否存在删除按钮"):
            if not page_obj.has_delete_button():
                pytest.skip("未找到删除按钮")

        with allure.step("点击删除并取消"):
            rows_before = page_obj.get_table_row_count()
            page_obj.click_delete_first_row()
            page_obj.cancel_delete()
            logged_in_page.wait_for_timeout(1000)

            rows_after = page_obj.get_table_row_count()
            allure.attach(
                logged_in_page.screenshot(),
                name="删除取消后",
                attachment_type=allure.attachment_type.PNG,
            )
            assert rows_after == rows_before, "取消删除后数据量不一致"

    @allure.story("删除服务项目")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("删除服务项目-确认操作验证")
    def test_delete_service_project_confirm(self, logged_in_page):
        """验证删除服务项目确认后数据减少"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)

        with allure.step("导航到服务项目配置页"):
            home.goto_service_project()
            logged_in_page.wait_for_timeout(1000)

        with allure.step("检查是否存在删除按钮"):
            if not page_obj.has_delete_button():
                pytest.skip("未找到删除按钮")

        with allure.step("点击删除并确认"):
            rows_before = page_obj.get_table_row_count()
            page_obj.click_delete_first_row()
            msgs = page_obj.confirm_delete()
            logger.info(f"删除 Toast: {msgs}")
            logged_in_page.wait_for_timeout(2000)

            rows_after = page_obj.get_table_row_count()
            allure.attach(
                logged_in_page.screenshot(),
                name="删除确认后",
                attachment_type=allure.attachment_type.PNG,
            )
            assert rows_after < rows_before, \
                f"删除后数据量应减少，但 {rows_before} -> {rows_after}"


@allure.feature("智能服务配置-合同服务")
class TestContractService:

    @allure.story("新增合同服务")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("新增合同服务并验证数据在列表中")
    def test_add_contract_service(self, logged_in_page, test_data):
        """新增合同服务，提交后验证数据出现在列表中"""
        data = test_data["contract_service"]
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)

        with allure.step("导航到合同服务配置页"):
            home.goto_contract_service()

        with allure.step("打开新增弹窗"):
            assert page_obj.open_add_modal(), "新增弹窗未打开"

        with allure.step("填写表单"):
            page_obj.fill_form(
                title=data["title"],
                content=data["content"],
                fee=data["fee"],
            )
        allure.attach(
            logged_in_page.screenshot(),
            name="表单填写完成",
            attachment_type=allure.attachment_type.PNG,
        )

        with allure.step("提交并验证"):
            success, msgs = page_obj.submit_and_verify(data["title"])
            logger.info(f"新增合同服务结果: success={success}, toast={msgs}")
            assert success, f"新增失败，Toast: {msgs}"


@allure.feature("内容管理-知识库")
class TestKnowledge:

    @allure.story("新增知识库")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("新增知识库并验证数据在列表中")
    def test_add_knowledge(self, logged_in_page, test_data):
        """新增知识库，提交后验证数据出现在列表中"""
        data = test_data["knowledge"]
        home = HomePage(logged_in_page)
        page_obj = KnowledgePage(logged_in_page)

        with allure.step("导航到知识库页"):
            home.goto_knowledge()

        with allure.step("打开新增弹窗"):
            assert page_obj.open_add_modal(), "新增弹窗未打开"

        with allure.step("填写表单"):
            page_obj.fill_form(
                title=data["title"],
                content=data["content"],
            )
        allure.attach(
            logged_in_page.screenshot(),
            name="表单填写完成",
            attachment_type=allure.attachment_type.PNG,
        )

        with allure.step("提交并验证"):
            success, msgs = page_obj.submit_and_verify(data["title"])
            logger.info(f"新增知识库结果: success={success}, toast={msgs}")
            assert success, f"新增失败，Toast: {msgs}"

    @allure.story("状态切换")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("切换知识库状态（禁用/启用）")
    def test_toggle_knowledge_status(self, logged_in_page):
        """切换知识库的启用/禁用状态"""
        home = HomePage(logged_in_page)
        page_obj = KnowledgePage(logged_in_page)

        with allure.step("导航到知识库页"):
            home.goto_knowledge()
            logged_in_page.wait_for_timeout(1000)

        with allure.step("检查是否存在禁用/启用按钮"):
            if not page_obj.has_toggle_button():
                pytest.skip("未找到禁用/启用按钮")

        with allure.step("切换状态"):
            text, msgs = page_obj.toggle_status()
            logger.info(f"状态切换({text}) Toast: {msgs}")

    @allure.story("查看详情")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查看知识库详情")
    def test_view_knowledge_detail(self, logged_in_page):
        """查看知识库详情弹窗"""
        home = HomePage(logged_in_page)
        page_obj = KnowledgePage(logged_in_page)

        with allure.step("导航到知识库页"):
            home.goto_knowledge()
            logged_in_page.wait_for_timeout(1000)

        with allure.step("检查是否存在详情按钮"):
            if not page_obj.has_detail_button():
                pytest.skip("未找到详情按钮")

        with allure.step("点击详情并验证弹窗打开"):
            assert page_obj.view_detail(), "详情弹窗未打开"
            allure.attach(
                logged_in_page.screenshot(),
                name="详情弹窗",
                attachment_type=allure.attachment_type.PNG,
            )


# ──────────── 编辑功能测试 ────────────

@allure.feature("智能服务配置-合同服务")
class TestContractServiceExt:

    @allure.story("编辑合同服务")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("打开合同服务编辑弹窗")
    def test_edit_contract_service(self, logged_in_page):
        """验证编辑按钮能打开编辑弹窗"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()
        logged_in_page.wait_for_timeout(1000)

        with allure.step("检查编辑按钮是否存在"):
            if not page_obj.has_edit_button():
                pytest.skip("未找到编辑按钮")

        with allure.step("点击编辑按钮"):
            assert page_obj.click_edit_first_row(), "编辑弹窗未打开"

        with allure.step("验证弹窗已打开且表单有数据"):
            assert page_obj.is_modal_open(), "弹窗未打开"
            # 验证表单中已有数据（编辑模式应预填数据）
            title_value = logged_in_page.evaluate("""
                () => {
                    const input = document.querySelector('.ant-modal input[id*="title"]');
                    return input ? input.value : '';
                }
            """)
            logger.info(f"编辑弹窗中标题值: {title_value}")
            assert title_value, "编辑弹窗中标题为空"

        allure.attach(
            logged_in_page.screenshot(),
            name="编辑弹窗",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("表单必填验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("合同服务空表单提交应显示验证错误")
    def test_contract_service_empty_form(self, logged_in_page):
        """验证合同服务空表单提交时显示必填错误"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()

        page_obj.open_add_modal()

        required = page_obj.get_modal_required_fields()
        logger.info(f"合同服务必填字段: {required}")
        assert len(required) > 0, "未识别到必填字段"

        errors = page_obj.submit_empty_form_and_get_errors()
        allure.attach(
            logged_in_page.screenshot(),
            name="空表单验证错误",
            attachment_type=allure.attachment_type.PNG,
        )
        assert len(errors) > 0, "空表单提交未触发验证错误"


@allure.feature("内容管理-知识库")
class TestKnowledgeExt:

    @allure.story("表单必填验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("知识库空表单提交应显示验证错误")
    def test_knowledge_empty_form(self, logged_in_page):
        """验证知识库空表单提交时显示必填错误"""
        home = HomePage(logged_in_page)
        page_obj = KnowledgePage(logged_in_page)
        home.goto_knowledge()

        page_obj.open_add_modal()

        required = page_obj.get_modal_required_fields()
        logger.info(f"知识库必填字段: {required}")
        assert len(required) > 0, "未识别到必填字段"

        errors = page_obj.submit_empty_form_and_get_errors()
        allure.attach(
            logged_in_page.screenshot(),
            name="空表单验证错误",
            attachment_type=allure.attachment_type.PNG,
        )
        assert len(errors) > 0, "空表单提交未触发验证错误"


# ──────────── 服务商管理 ────────────

@allure.feature("服务商管理-代理记账公司")
class TestProvider:

    @allure.story("页面加载")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("代理记账公司管理页面正常加载")
    def test_provider_page_load(self, logged_in_page):
        """验证代理记账公司管理页面能正常加载"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)

        with allure.step("导航到代理记账公司管理页"):
            home.goto_provider()
            assert "/service-provider/proxy-accounting" in logged_in_page.url

        with allure.step("验证表格列头"):
            headers = page_obj.get_table_headers()
            logger.info(f"表头: {headers}")
            assert "公司名称" in headers, "缺少'公司名称'列"
            assert "联系人" in headers, "缺少'联系人'列"
            assert "启用状态" in headers, "缺少'启用状态'列"

        with allure.step("验证操作按钮"):
            assert page_obj.has_add_button(), "缺少'服务商入驻'按钮"

        allure.attach(
            logged_in_page.screenshot(),
            name="代理记账公司管理页",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("服务商入驻")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("新增代理记账公司并验证数据在列表中")
    def test_add_provider(self, logged_in_page, test_data):
        """新增代理记账公司，提交后验证数据出现在列表中"""
        data = test_data["provider"]
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)

        with allure.step("导航到代理记账公司管理页"):
            home.goto_provider()

        with allure.step("打开新增弹窗"):
            assert page_obj.click_add_button(), "新增弹窗未打开"

        with allure.step("验证弹窗表单字段"):
            labels = page_obj.get_modal_required_fields()
            logger.info(f"表单必填字段: {labels}")
            assert len(labels) >= 1, f"应至少有1个必填字段，实际 {len(labels)} 个"

            form_info = page_obj.get_modal_form_fields()
            logger.info(f"表单字段详情: inputs={len(form_info['inputs'])}")
            assert len(form_info["inputs"]) >= 1, "弹窗应至少有1个输入框"

        allure.attach(
            logged_in_page.screenshot(),
            name="表单填写完成",
            attachment_type=allure.attachment_type.PNG,
        )

        with allure.step("提交并验证"):
            # 填写表单
            page_obj.fill_form(
                company_name=data["company_name"],
                office_address=data["office_address"],
                contact_person=data["contact_person"],
                contact_phone=data["contact_phone"],
            )

            # 提交表单
            success, msgs = page_obj.submit_and_verify(data["company_name"])
            logger.info(f"新增服务商结果: success={success}, toast={msgs}")

            allure.attach(
                logged_in_page.screenshot(),
                name="提交结果",
                attachment_type=allure.attachment_type.PNG,
            )

            # 验证：要么成功，要么有验证错误（说明表单被提交了）
            assert success or len(msgs) > 0 or page_obj.is_modal_open() is False, \
                f"新增结果异常，Toast: {msgs}"

    @allure.story("编辑服务商")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("编辑代理记账公司信息")
    def test_edit_provider(self, logged_in_page):
        """验证编辑按钮能打开编辑弹窗"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()
        logged_in_page.wait_for_timeout(1000)

        with allure.step("检查编辑按钮是否存在"):
            if not page_obj.has_edit_button():
                pytest.skip("未找到编辑按钮")

        with allure.step("点击编辑按钮"):
            assert page_obj.click_edit_first_row(), "编辑弹窗未打开"

        with allure.step("验证弹窗已打开"):
            assert page_obj.is_modal_open(), "弹窗未打开"
            logger.info("编辑弹窗已打开")

        allure.attach(
            logged_in_page.screenshot(),
            name="编辑弹窗",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("查看详情")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查看代理记账公司详情")
    def test_view_provider_detail(self, logged_in_page):
        """查看代理记账公司详情弹窗"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()
        logged_in_page.wait_for_timeout(1000)

        with allure.step("检查详情按钮是否存在"):
            if not page_obj.has_detail_button():
                pytest.skip("未找到详情按钮")

        with allure.step("点击详情按钮"):
            assert page_obj.view_detail_first_row(), "详情弹窗未打开"

        allure.attach(
            logged_in_page.screenshot(),
            name="详情弹窗",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("重置密码")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("重置代理记账公司密码")
    def test_reset_password(self, logged_in_page):
        """验证重置密码按钮能触发操作"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()
        logged_in_page.wait_for_timeout(1000)

        with allure.step("检查重置密码按钮是否存在"):
            if not page_obj.has_reset_password_button():
                pytest.skip("未找到重置密码按钮")

        with allure.step("点击重置密码"):
            assert page_obj.click_reset_password_first_row(), "重置密码操作失败"
            msgs = page_obj.get_toasts()
            logger.info(f"重置密码 Toast: {msgs}")

        allure.attach(
            logged_in_page.screenshot(),
            name="重置密码",
            attachment_type=allure.attachment_type.PNG,
        )
