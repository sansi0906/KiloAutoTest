# -*- coding: utf-8 -*-
"""
UI 元素及交互验证测试用例

覆盖：
  - 页面标题、表头、搜索框、分页等 UI 元素存在性
  - 弹窗交互（打开/取消关闭/ESC关闭）
  - 表单必填验证
  - 搜索功能
"""
import pytest
import allure

from pages.home_page import HomePage
from pages.service_project_page import ServiceProjectPage
from pages.contract_service_page import ContractServicePage
from pages.knowledge_page import KnowledgePage
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
        """验证ESC键能关闭弹窗"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        assert page_obj.open_add_modal(), "新增弹窗未打开"
        page_obj.close_modal_by_esc()
        logged_in_page.wait_for_timeout(1000)
        assert not page_obj.is_modal_open(), "ESC后弹窗未关闭"

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


# ──────────── 搜索功能验证 ────────────

@allure.feature("UI验证")
@allure.story("搜索功能")
class TestSearchFunction:

    @allure.title("服务项目-搜索功能验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_service_project(self, logged_in_page):
        """验证搜索能过滤表格数据"""
        home = HomePage(logged_in_page)
        page_obj = ServiceProjectPage(logged_in_page)
        home.goto_service_project()

        # 记录搜索前行数
        rows_before = page_obj.get_table_row_count()
        logger.info(f"搜索前行数: {rows_before}")

        # 搜索一个不存在的关键词
        page_obj.search("zzzznonexist", "top-query-form_itemName")
        rows_after = page_obj.get_table_row_count()
        logger.info(f"搜索后行数: {rows_after}")

        allure.attach(
            logged_in_page.screenshot(),
            name="搜索结果截图",
            attachment_type=allure.attachment_type.PNG,
        )

        assert rows_after == 0, f"搜索不存在的关键词应返回0条，实际{rows_after}"

        # 清空搜索，验证数据恢复
        page_obj.clear_search("top-query-form_itemName")
        rows_cleared = page_obj.get_table_row_count()
        assert rows_cleared > 0, "清空搜索后数据未恢复"
