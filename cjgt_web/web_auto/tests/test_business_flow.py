# -*- coding: utf-8 -*-
"""
业务流程测试用例 —— 覆盖服务项目、合同服务、知识库的新增等操作
"""
import pytest
import allure

from pages.home_page import HomePage
from pages.service_project_page import ServiceProjectPage
from pages.contract_service_page import ContractServicePage
from pages.knowledge_page import KnowledgePage
from utils.logger import logger


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
