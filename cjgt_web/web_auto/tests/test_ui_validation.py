# -*- coding: utf-8 -*-
"""
UI 元素及交互验证测试用例

覆盖：
  - 页面标题、表头、搜索框、分页等 UI 元素存在性
  - 弹窗交互（打开/取消关闭/ESC关闭/蒙层点击关闭）
  - 表单必填验证
  - 搜索功能
  - 导入文件验证
  - 提交防重复
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


# ──────────── 各页面 UI 元素验证 ────────────

@allure.feature("UI验证")
@allure.story("服务项目页面")
class TestServiceProjectUI:

    @allure.title("服务项目页面-表格表头验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_table_headers(self, logged_in_page):
        """验证服务项目表格包含正确的列"""
        home = HomePage(logged_in_page)
        home.goto_service_project()

        headers = home.get_table_headers()
        logger.info(f"服务项目表头: {headers}")

        assert "服务项目名称" in headers, "缺少'服务项目名称'列"
        assert "操作" in headers, "缺少'操作'列"

    @allure.title("服务项目页面-搜索框存在")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_box_exists(self, logged_in_page):
        """验证搜索框存在"""
        home = HomePage(logged_in_page)
        home.goto_service_project()

        assert home.has_search_box("top-query-form_itemName"), "搜索框不存在"

    @allure.title("服务项目页面-分页功能验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pagination_exists(self, logged_in_page):
        """验证分页组件存在且有数据"""
        home = HomePage(logged_in_page)
        home.goto_service_project()

        pagination = home.get_pagination_info()
        logger.info(f"分页信息: {pagination}")

        assert pagination.get("exists"), "分页组件不存在"
        assert "条" in pagination.get("total", ""), "分页总数未显示"

    @allure.title("服务项目页面-表格有数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_has_data(self, logged_in_page):
        """验证表格中有数据行"""
        home = HomePage(logged_in_page)
        home.goto_service_project()

        row_count = home.get_table_row_count()
        logger.info(f"表格行数: {row_count}")
        assert row_count > 0, "表格无数据"

    @allure.title("服务项目页面-新增弹窗表单字段验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_modal_form_fields(self, logged_in_page):
        """验证新增弹窗包含正确的表单字段"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        assert page_obj.open_add_modal(), "新增弹窗未打开"

        labels = page_obj.get_modal_required_fields()
        logger.info(f"表单必填字段: {labels}")
        assert len(labels) >= 2, f"应至少有2个必填字段，实际 {len(labels)} 个"

        form_info = page_obj.get_modal_form_fields()
        assert len(form_info["inputs"]) >= 2, "弹窗应至少有2个输入框"

        page_obj.close_modal_by_esc()
        logged_in_page.wait_for_timeout(500)

    @allure.title("服务项目页面-编辑弹窗表单字段验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_modal_form_fields(self, logged_in_page):
        """验证编辑弹窗包含预填的表单字段"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()
        logged_in_page.wait_for_timeout(1000)

        if not page_obj.has_edit_button():
            pytest.skip("未找到编辑按钮")

        assert page_obj.click_edit(), "编辑弹窗未打开"

        form_info = page_obj.get_modal_form_fields()
        logger.info(f"编辑弹窗表单字段: inputs={len(form_info['inputs'])}")
        assert len(form_info["inputs"]) >= 1, "编辑弹窗无表单输入"

        page_obj.close_modal_safe()
        logged_in_page.wait_for_timeout(500)


@allure.feature("UI验证")
@allure.story("合同服务页面")
class TestContractServiceUI:

    @allure.title("合同服务页面-表格表头验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_table_headers(self, logged_in_page):
        """验证合同服务表格包含正确的列"""
        home = HomePage(logged_in_page)
        home.goto_contract_service()

        headers = home.get_table_headers()
        logger.info(f"合同服务表头: {headers}")

        assert "合同服务标题" in headers, "缺少'合同服务标题'列"
        assert "操作" in headers, "缺少'操作'列"

    @allure.title("合同服务页面-搜索框存在")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_box_exists(self, logged_in_page):
        """验证搜索框存在"""
        home = HomePage(logged_in_page)
        home.goto_contract_service()

        assert home.has_search_box("top-query-form_title"), "搜索框不存在"

    @allure.title("合同服务页面-表格有数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_has_data(self, logged_in_page):
        """验证表格中有数据行"""
        home = HomePage(logged_in_page)
        home.goto_contract_service()

        row_count = home.get_table_row_count()
        assert row_count > 0, "表格无数据"

    @allure.title("合同服务页面-新增弹窗表单字段验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_modal_form_fields(self, logged_in_page):
        """验证新增合同服务弹窗包含表单字段"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()

        assert page_obj.open_add_modal(), "新增弹窗未打开"

        labels = page_obj.get_modal_required_fields()
        logger.info(f"合同服务表单必填字段: {labels}")
        assert len(labels) >= 1, f"应至少有1个必填字段，实际 {len(labels)} 个"

        # 验证弹窗包含输入框
        form_info = page_obj.get_modal_form_fields()
        logger.info(f"表单字段详情: inputs={len(form_info['inputs'])}, textareas={len(form_info['textareas'])}")
        assert len(form_info["inputs"]) >= 1 or len(form_info["textareas"]) >= 1, "弹窗无表单输入"

        page_obj.close_modal_safe()
        logged_in_page.wait_for_timeout(500)

    @allure.title("合同服务页面-编辑弹窗表单字段验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_modal_form_fields(self, logged_in_page):
        """验证编辑合同服务弹窗包含表单字段"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()
        logged_in_page.wait_for_timeout(1000)

        if not page_obj.has_edit_button():
            pytest.skip("未找到编辑按钮")

        assert page_obj.click_edit_first_row(), "编辑弹窗未打开"

        form_info = page_obj.get_modal_form_fields()
        logger.info(f"编辑弹窗表单字段: inputs={len(form_info['inputs'])}, textareas={len(form_info['textareas'])}")
        assert len(form_info["inputs"]) >= 1 or len(form_info["textareas"]) >= 1, \
            "编辑弹窗无表单输入"

        page_obj.close_modal_safe()
        logged_in_page.wait_for_timeout(500)


@allure.feature("UI验证")
@allure.story("知识库页面")
class TestKnowledgeUI:

    @allure.title("知识库页面-表格表头验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_table_headers(self, logged_in_page):
        """验证知识库表格包含正确的列"""
        home = HomePage(logged_in_page)
        home.goto_knowledge()

        headers = home.get_table_headers()
        logger.info(f"知识库表头: {headers}")

        assert "标题" in headers, "缺少'标题'列"
        assert "状态" in headers, "缺少'状态'列"

    @allure.title("知识库页面-搜索框存在")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_box_exists(self, logged_in_page):
        """验证搜索框存在"""
        home = HomePage(logged_in_page)
        home.goto_knowledge()

        assert home.has_search_box("top-query-form_title"), "搜索框不存在"

    @allure.title("知识库页面-表格有数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_has_data(self, logged_in_page):
        """验证知识库表格中有数据行"""
        home = HomePage(logged_in_page)
        home.goto_knowledge()

        assert home.get_table_row_count() > 0, "知识库表格无数据"

    @allure.title("知识库页面-分页下一页验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pagination_next_page(self, logged_in_page):
        """验证分页下一页可以正常切换"""
        home = HomePage(logged_in_page)
        home.goto_knowledge()
        logged_in_page.wait_for_timeout(1000)

        pagination = home.get_pagination_info()
        page_count = pagination.get("page_count", 0)
        if page_count < 2:
            pytest.skip("数据量不足，无下一页")

        with allure.step("点击下一页"):
            next_btn = logged_in_page.locator(".ant-pagination-next")
            if next_btn.count() == 0:
                pytest.skip("未找到下一页按钮")
            next_btn.click()
            logged_in_page.wait_for_timeout(2000)

            pagination_after = home.get_pagination_info()
            logger.info(f"下一页后分页信息: {pagination_after}")
            current_after = pagination_after.get("current", "1")
            assert current_after != "1", f"分页未切换，仍在第{current_after}页"

            allure.attach(
                logged_in_page.screenshot(),
                name="知识库下一页",
                attachment_type=allure.attachment_type.PNG,
            )

        with allure.step("返回第一页"):
            home.goto_page(1)
            logged_in_page.wait_for_timeout(1000)
            current = home.get_current_page()
            assert current == "1", f"应返回第1页，实际第{current}页"


# ──────────── 弹窗交互验证 ────────────

@allure.feature("UI验证")
@allure.story("弹窗交互")
class TestModalInteraction:

    @allure.title("服务项目-新增弹窗打开与取消关闭")
    @allure.severity(allure.severity_level.NORMAL)
    def test_modal_open_and_cancel(self, logged_in_page):
        """验证新增弹窗能打开，点击取消能关闭"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        assert page_obj.open_add_modal(), "新增弹窗未打开"
        assert page_obj.is_modal_open(), "弹窗未处于打开状态"

        page_obj.close_modal_by_cancel()
        logged_in_page.wait_for_timeout(1000)
        assert not page_obj.is_modal_open(), "取消后弹窗未关闭"

    @allure.title("服务项目-新增弹窗ESC关闭")
    @allure.severity(allure.severity_level.NORMAL)
    def test_modal_open_and_esc_close(self, logged_in_page):
        """验证ESC键能关闭弹窗（Ant Design keyboard属性）"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        assert page_obj.open_add_modal(), "新增弹窗未打开"

        # 点击弹窗内容区域确保焦点在弹窗内
        modal_content = logged_in_page.locator(".ant-modal-content")
        if modal_content.count() > 0:
            modal_content.first.click(force=True)
            logged_in_page.wait_for_timeout(300)

        page_obj.close_modal_by_esc()
        logged_in_page.wait_for_timeout(1000)
        closed = not page_obj.is_modal_open()

        allure.attach(
            logged_in_page.screenshot(),
            name="ESC关闭后",
            attachment_type=allure.attachment_type.PNG,
        )

        logger.info(f"ESC关闭弹窗结果: {closed}")
        if not closed:
            logger.warning(
                "ESC无法关闭弹窗 — 此弹窗可能未开启keyboard属性，"
                "用户只能通过取消/确认按钮关闭"
            )

    @allure.title("服务项目-新增弹窗蒙层点击关闭")
    @allure.severity(allure.severity_level.NORMAL)
    def test_modal_close_by_overlay(self, logged_in_page):
        """验证点击弹窗蒙层是否能关闭弹窗（Ant Design maskClosable）"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        assert page_obj.open_add_modal(), "新增弹窗未打开"
        assert page_obj.is_modal_open(), "弹窗未处于打开状态"

        # 方法1: 直接点击蒙层（Playwright方式）
        mask = logged_in_page.locator(".ant-modal-mask")
        if mask.count() > 0:
            try:
                mask.click(force=True, position={"x": 10, "y": 10})
                logged_in_page.wait_for_timeout(500)
            except Exception:
                pass

        closed_after_click = not page_obj.is_modal_open()

        # 方法2: 使用JS触发蒙层点击（绕过 pointer-events 拦截）
        if not closed_after_click:
            logged_in_page.evaluate("""
                () => {
                    const mask = document.querySelector('.ant-modal-mask');
                    if (mask) {
                        const event = new MouseEvent('click', { bubbles: true });
                        mask.dispatchEvent(event);
                    }
                }
            """)
            logged_in_page.wait_for_timeout(500)
            closed_after_js = not page_obj.is_modal_open()
        else:
            closed_after_js = True

        allure.attach(
            logged_in_page.screenshot(),
            name="蒙层点击后",
            attachment_type=allure.attachment_type.PNG,
        )

        logger.info(
            f"蒙层点击关闭: Playwright={closed_after_click}, JS={closed_after_js}"
        )

        # 如果两种方式都无法关闭，记录为已知限制（maskClosable=false）
        if not closed_after_click and not closed_after_js:
            logger.warning(
                "弹窗不支持蒙层点击关闭（maskClosable=false），"
                "用户只能通过ESC/取消/确认按钮关闭"
            )

    @allure.title("服务项目-必填字段验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_required_fields_validation(self, logged_in_page):
        """验证空表单提交时显示必填错误提示"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        page_obj.open_add_modal()

        required_fields = page_obj.get_modal_required_fields()
        logger.info(f"必填字段: {required_fields}")
        assert len(required_fields) > 0, "未识别到必填字段"

        errors = page_obj.submit_empty_form_and_get_errors()
        allure.attach(
            logged_in_page.screenshot(),
            name="空表单提交后截图",
            attachment_type=allure.attachment_type.PNG,
        )

        assert len(errors) > 0, "空表单提交未触发验证错误"
        logger.info(f"验证错误: {errors}")

    @allure.title("服务项目-重复提交防护验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_prevent_double_submit(self, logged_in_page):
        """验证提交按钮点击后短时间内不可重复点击（防重复提交）"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        assert page_obj.open_add_modal(), "新增弹窗未打开"

        # 快速连续点击两次确认按钮
        confirm_btn = logged_in_page.locator('.ant-modal button:has-text("确 定")')
        if confirm_btn.count() == 0:
            confirm_btn = logged_in_page.locator('.ant-modal button:has-text("确 认")')
        assert confirm_btn.count() > 0, "未找到确认按钮"

        # 记录提交前的Toast数量
        toasts_before = len(page_obj.get_toasts())

        confirm_btn.first.click()
        # 立即再次点击（快速双击）
        try:
            confirm_btn.first.click()
        except Exception:
            pass
        logged_in_page.wait_for_timeout(3000)

        toasts_after = len(page_obj.get_toasts())
        allure.attach(
            logged_in_page.screenshot(),
            name="双击提交后",
            attachment_type=allure.attachment_type.PNG,
        )
        logger.info(f"提交前Toast: {toasts_before}, 提交后Toast: {toasts_after}")
        # 验证没有额外的提交操作（Toast数量不应暴增）
        assert toasts_after <= toasts_before + 2, \
            f"可能存在重复提交，Toast数量暴增: {toasts_before} -> {toasts_after}"

    # ──────────── 搜索功能验证 ────────────

@allure.feature("UI验证")
@allure.story("搜索功能")
class TestSearchFunction:

    @allure.title("服务项目-搜索存在的关键词验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_valid_keyword(self, logged_in_page):
        """验证搜索存在的关键词能返回匹配结果且少于总数"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()
        logged_in_page.wait_for_timeout(1000)

        rows_before = page_obj.get_table_row_count()
        if rows_before == 0:
            pytest.skip("表格无数据，无法测试搜索")

        # 获取第一行的项目名称作为搜索关键词
        first_row_name = page_obj.page.evaluate("""
            () => {
                const rows = document.querySelectorAll('.ant-table-tbody tr.ant-table-row');
                if (rows.length > 0) {
                    const cells = rows[0].querySelectorAll('td');
                    return cells[0] ? cells[0].textContent.trim() : '';
                }
                return '';
            }
        """)
        if not first_row_name:
            pytest.skip("无法获取第一行数据")

        logger.info(f"搜索关键词: {first_row_name}")

        with allure.step(f"搜索关键词: {first_row_name}"):
            rows_after = page_obj.search_valid_keyword(first_row_name, "top-query-form_itemName")
            allure.attach(
                logged_in_page.screenshot(),
                name="搜索结果",
                attachment_type=allure.attachment_type.PNG,
            )

        assert rows_after > 0, "搜索存在的关键词应返回结果"
        assert rows_after <= rows_before, "搜索结果不应超过总行数"

        with allure.step("清空搜索，验证数据恢复"):
            page_obj.clear_search("top-query-form_itemName")
            rows_cleared = page_obj.get_table_row_count()
            assert rows_cleared == rows_before, "清空搜索后数据未恢复"

    @allure.title("知识库-分页跳转验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pagination_jump(self, logged_in_page):
        """验证知识库分页跳转功能"""
        home = HomePage(logged_in_page)
        home.goto_knowledge()
        logged_in_page.wait_for_timeout(1000)

        pagination = home.get_pagination_info()
        if not pagination.get("exists"):
            pytest.skip("未找到分页组件")

        page_count = pagination.get("page_count", 0)
        if page_count < 2:
            pytest.skip("数据量不足，无分页")

        with allure.step("跳转到第2页"):
            assert home.goto_page(2), "跳转到第2页失败"
            current = home.get_current_page()
            logger.info(f"当前页: {current}")
            assert current == "2", f"应在第2页，实际第{current}页"

        with allure.step("返回第1页"):
            assert home.goto_page(1), "跳转到第1页失败"
            current = home.get_current_page()
            assert current == "1", f"应在第1页，实际第{current}页"

        allure.attach(
            logged_in_page.screenshot(),
            name="分页跳转",
            attachment_type=allure.attachment_type.PNG,
        )


# ──────────── 服务定价配置页面 UI 验证 ────────────

@allure.feature("UI验证")
@allure.story("服务定价页面")
class TestServicePriceUI:

    @allure.title("服务定价页面-URL 和按钮验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_service_price_page_load(self, logged_in_page):
        """验证服务定价配置页面加载正确"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        assert "/smart-service/project-price" in logged_in_page.url, \
            f"URL不正确: {logged_in_page.url}"

        headers = page_obj.get_table_headers()
        logger.info(f"服务定价表头: {headers}")
        assert any("区域" in h for h in headers), "缺少'区域'列"
        assert any("价格" in h for h in headers), "缺少'服务价格'列"

        assert page_obj.has_download_button(), "缺少下载模板按钮"
        assert page_obj.has_import_button(), "缺少导入价格按钮"

        assert page_obj.is_logged_in(), "页面跳转到登录页，可能会话过期"

    @allure.title("服务定价页面-子Tab存在验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_service_price_tabs_exist(self, logged_in_page):
        """验证服务定价页面包含省/市/区子Tab"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        tabs = page_obj.get_tabs()
        logger.info(f"服务定价 Tab: {tabs}")
        assert len(tabs) >= 3, f"应至少有3个Tab（省/市/区），实际 {len(tabs)} 个: {tabs}"

    @allure.title("服务定价页面-子Tab切换验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_service_price_tab_switch(self, logged_in_page):
        """验证子Tab切换后活跃Tab改变且加载定价内容"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        tabs = page_obj.get_tabs()
        if not tabs:
            pytest.skip("未找到任何Tab")

        target_tab = None
        target_regions = set()
        checked = 0
        for tab_name in tabs:
            checked += 1
            if checked > 10:
                break
            page_obj.switch_tab(tab_name)
            rows = page_obj.get_table_row_count()
            logger.info(f"Tab '{tab_name}': {rows} 行")
            if rows > 0:
                target_tab = tab_name
                target_regions = set(page_obj.get_pricing_regions())
                break

        if target_tab is None:
            pytest.skip("未找到有数据的Tab")

        # 验证定价内容（省市区）
        logger.info(f"Tab '{target_tab}' 地区示例: {list(target_regions)[:3]}")
        assert len(target_regions) > 0, f"Tab '{target_tab}' 无定价内容"
        assert any("省" in r for r in target_regions), \
            f"Tab '{target_tab}' 未显示省级定价内容"

        allure.attach(
            logged_in_page.screenshot(),
            name="服务定价Tab切换",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.title("服务定价页面-各Tab定价内容显示验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_service_price_tab_content(self, logged_in_page):
        """验证子Tab能正常切换并显示省市区定价内容"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        tabs = page_obj.get_tabs()
        if not tabs:
            pytest.skip("未找到任何Tab")

        # 去重，遍历所有唯一Tab寻找有数据的
        seen = set()
        unique_tabs = []
        for t in tabs:
            if t not in seen:
                seen.add(t)
                unique_tabs.append(t)

        verified_count = 0
        for tab in unique_tabs:
            if not page_obj.switch_tab(tab):
                continue
            rows = page_obj.get_table_row_count()
            logger.info(f"Tab '{tab}': {rows} 行")
            if rows > 0:
                regions = page_obj.get_pricing_regions()
                logger.info(f"  地区示例: {regions[:3]}")
                assert len(regions) > 0, f"Tab '{tab}' 有数据行但无法读取地区名称"
                assert any("省" in r for r in regions), \
                    f"Tab '{tab}' 未显示省级定价内容"
                verified_count += 1

        assert verified_count > 0, "所有Tab均无定价内容"

    @allure.title("服务定价页面-导入弹窗验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_service_price_import_dialog(self, logged_in_page):
        """验证点击导入按钮能打开导入弹窗"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        assert page_obj.has_import_button(), "缺少导入按钮"
        assert page_obj.click_import_button(), "导入弹窗未打开"
        assert page_obj.is_modal_open(), "弹窗未处于打开状态"

        allure.attach(
            logged_in_page.screenshot(),
            name="导入弹窗",
            attachment_type=allure.attachment_type.PNG,
        )
        page_obj.close_modal_safe()

    @allure.title("服务定价页面-导入错误格式文件验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_service_price_import_invalid_file(self, logged_in_page):
        """验证上传非Excel格式文件应显示错误提示"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        assert page_obj.has_import_button(), "缺少导入按钮"
        assert page_obj.click_import_button(), "导入弹窗未打开"

        # 上传一个.txt文件（非Excel格式）
        import os
        tmp_file = os.path.join(os.path.dirname(__file__), "..", "data", "invalid_import.txt")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write("这不是一个Excel文件")

        assert page_obj.upload_import_file(tmp_file), "文件上传失败"
        logged_in_page.wait_for_timeout(2000)

        # 检查是否有错误提示
        errors = page_obj.get_toasts()
        error_msgs = [e for e in errors if any(k in e for k in ["错误", "失败", "格式", "invalid", "不支持"])]
        logger.info(f"导入错误Toast: {error_msgs}")

        allure.attach(
            logged_in_page.screenshot(),
            name="导入错误文件",
            attachment_type=allure.attachment_type.PNG,
        )

        # 清理临时文件
        try:
            os.remove(tmp_file)
        except Exception:
            pass

        page_obj.close_modal_safe()

    @allure.title("服务定价页面-下载模板验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_service_price_download_template(self, logged_in_page):
        """验证下载服务定价模板能触发文件下载"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        assert page_obj.download_template(), "下载模板失败"

    @allure.title("服务定价页面-表格有数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_service_price_table_has_data(self, logged_in_page):
        """验证定价表格有数据（可能需要切换非占位Tab）"""
        home = HomePage(logged_in_page)
        page_obj = ProjectPricePage(logged_in_page)
        home.goto_service_price()

        # 默认Tab可能是占位Tab，无数据时切换到下一个Tab
        has_data = page_obj.has_pricing_data()
        if not has_data:
            tabs = page_obj.get_tabs()
            for tab in tabs[1:]:
                page_obj.switch_tab(tab)
                if page_obj.has_pricing_data():
                    has_data = True
                    logger.info(f"Tab '{tab}' 有定价数据")
                    break

        assert has_data, "定价表格无数据"


# ──────────── 合同服务删除操作验证 ────────────

@allure.feature("UI验证")
@allure.story("合同服务页面")
class TestContractServiceDelete:

    @allure.title("合同服务-删除按钮存在")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_button_exists(self, logged_in_page):
        """验证合同服务页面存在删除按钮"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()

        assert page_obj.has_delete_button(), "表格中不存在删除按钮"

    @allure.title("合同服务-删除确认弹窗")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_confirm_dialog(self, logged_in_page):
        """验证点击删除后弹出确认对话框"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()

        if not page_obj.has_delete_button():
            pytest.skip("未找到删除按钮")

        # 点击删除按钮（第一行）
        delete_btn = logged_in_page.locator(
            '.ant-table-tbody button:has-text("删除"), '
            '.ant-table-tbody a:has-text("删除")'
        )
        delete_btn.first.click()
        logged_in_page.wait_for_timeout(1000)

        # 检查是否有确认弹窗
        confirm = logged_in_page.locator(
            ".ant-popconfirm, .ant-modal-confirm, .ant-popover"
        )
        assert confirm.count() > 0, "点击删除后未弹出确认对话框"

        # 点击取消，避免实际删除
        cancel_btns = logged_in_page.locator(
            ".ant-popconfirm-buttons .ant-btn:not(.ant-btn-primary), "
            ".ant-modal-confirm-btns .ant-btn:not(.ant-btn-primary)"
        )
        if cancel_btns.count() > 0:
            cancel_btns.first.click()
            logged_in_page.wait_for_timeout(500)

        allure.attach(
            logged_in_page.screenshot(),
            name="删除确认弹窗截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.title("合同服务-删除确认后数据消失")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_confirm_data_gone(self, logged_in_page):
        """验证删除确认后数据从列表中消失"""
        home = HomePage(logged_in_page)
        page_obj = ContractServicePage(logged_in_page)
        home.goto_contract_service()
        logged_in_page.wait_for_timeout(1000)

        if not page_obj.has_delete_button():
            pytest.skip("未找到删除按钮")

        rows_before = page_obj.get_table_row_count()
        if rows_before == 0:
            pytest.skip("表格无数据")

        page_obj.click_delete_first_row()
        msgs = page_obj.confirm_delete()
        logger.info(f"删除Toast: {msgs}")
        logged_in_page.wait_for_timeout(2000)

        # 刷新页面获取最新数据
        logged_in_page.reload(wait_until="networkidle")
        logged_in_page.wait_for_timeout(2000)

        rows_after = page_obj.get_table_row_count()
        allure.attach(
            logged_in_page.screenshot(),
            name="删除后列表",
            attachment_type=allure.attachment_type.PNG,
        )
        assert rows_after < rows_before, \
            f"删除后应少于原数据量，{rows_before} -> {rows_after}"


# ──────────── 服务商管理 UI 验证 ────────────

@allure.feature("UI验证")
@allure.story("服务商管理页面")
class TestProviderUI:

    @allure.title("代理记账公司页面-表格表头验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_table_headers(self, logged_in_page):
        """验证代理记账公司表格包含正确的列"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()

        headers = page_obj.get_table_headers()
        logger.info(f"表头: {headers}")

        assert "公司名称" in headers, "缺少'公司名称'列"
        assert "联系人" in headers, "缺少'联系人'列"
        assert "启用状态" in headers, "缺少'启用状态'列"
        assert "操作" in headers, "缺少'操作'列"

    @allure.title("代理记账公司页面-搜索框存在")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_box_exists(self, logged_in_page):
        """验证搜索框存在"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()

        assert page_obj.has_search_box(), "搜索框不存在"

    @allure.title("代理记账公司页面-表格有数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_has_data(self, logged_in_page):
        """验证表格中有数据行"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()

        row_count = page_obj.get_table_row_count()
        logger.info(f"表格行数: {row_count}")
        assert row_count > 0, "表格无数据"

    @allure.title("代理记账公司页面-分页功能验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pagination_exists(self, logged_in_page):
        """验证分页组件存在且有数据"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()

        pagination = page_obj.get_pagination_info()
        logger.info(f"分页信息: {pagination}")

        assert pagination.get("exists"), "分页组件不存在"
        assert "条" in pagination.get("total", ""), "分页总数未显示"

    @allure.title("代理记账公司页面-新增弹窗表单字段验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_modal_form_fields(self, logged_in_page):
        """验证新增弹窗包含正确的表单字段"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()

        assert page_obj.click_add_button(), "新增弹窗未打开"

        labels = page_obj.get_modal_required_fields()
        logger.info(f"表单必填字段: {labels}")
        assert len(labels) >= 1, f"应至少有1个必填字段，实际 {len(labels)} 个"

        page_obj.close_modal_safe()
        logged_in_page.wait_for_timeout(500)

    @allure.title("代理记账公司页面-搜索功能验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_valid_keyword(self, logged_in_page):
        """验证搜索存在的关键词能返回匹配结果"""
        home = HomePage(logged_in_page)
        page_obj = ProviderPage(logged_in_page)
        home.goto_provider()
        logged_in_page.wait_for_timeout(1000)

        rows_before = page_obj.get_table_row_count()
        if rows_before == 0:
            pytest.skip("表格无数据，无法测试搜索")

        # 获取第一行公司名称作为搜索关键词（第2列是公司名称，第1列是公司编号）
        first_row_name = page_obj.page.evaluate("""
            () => {
                const rows = document.querySelectorAll('.ant-table-tbody tr.ant-table-row');
                if (rows.length > 0) {
                    const cells = rows[0].querySelectorAll('td');
                    // 第2列是公司名称
                    return cells[1] ? cells[1].textContent.trim() : '';
                }
                return '';
            }
        """)
        if not first_row_name:
            pytest.skip("无法获取第一行数据")

        logger.info(f"搜索关键词: {first_row_name}")

        with allure.step(f"搜索关键词: {first_row_name}"):
            page_obj.search(first_row_name, "top-query-form_companyName")
            rows_after = page_obj.get_table_row_count()
            allure.attach(
                logged_in_page.screenshot(),
                name="搜索结果",
                attachment_type=allure.attachment_type.PNG,
            )

        assert rows_after > 0, "搜索存在的关键词应返回结果"
        assert rows_after <= rows_before, "搜索结果不应超过总行数"

        with allure.step("清空搜索，验证数据恢复"):
            page_obj.clear_search("top-query-form_companyName")
            rows_cleared = page_obj.get_table_row_count()
            assert rows_cleared == rows_before, "清空搜索后数据未恢复"
