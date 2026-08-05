# -*- coding: utf-8 -*-
"""登录测试用例"""
import pytest
import allure

from config.env_config import USERNAME, PASSWORD
from pages.login_page import LoginPage


@allure.feature("登录")
class TestLogin:

    @allure.story("账号密码登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("使用正确的账号密码登录成功")
    def test_login_success(self, page):
        """验证正确账号密码能成功登录"""
        login_page = LoginPage(page)

        with allure.step("打开登录页并登录"):
            login_page.open()
            result = login_page.login(USERNAME, PASSWORD)

        with allure.step("验证登录成功"):
            assert result, f"登录失败，当前URL: {page.url}"

        allure.attach(
            page.screenshot(),
            name="登录后截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("错误密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("使用错误密码登录失败")
    def test_login_wrong_password(self, page):
        """验证错误密码登录失败"""
        login_page = LoginPage(page)
        login_page.open()

        with allure.step("填写正确用户名和错误密码"):
            login_page.page.locator('input[placeholder="账号"]').fill(USERNAME)
            login_page.page.locator('input[type="password"]').fill("wrong_pwd")

        with allure.step("点击登录"):
            login_page.page.locator('button:has-text("登 录")').click(force=True)
            page.wait_for_timeout(3000)

        with allure.step("验证仍在登录页"):
            assert "login" in page.url.lower() or "adminlogin" in page.url.lower(), \
                "错误密码后应仍在登录页"

        allure.attach(
            page.screenshot(),
            name="登录失败截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("空账号登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("不填账号直接登录应失败")
    def test_login_empty_username(self, page):
        """验证空账号时登录应失败"""
        login_page = LoginPage(page)
        login_page.open()

        with allure.step("只填密码不填账号"):
            login_page.page.locator('input[type="password"]').fill(PASSWORD)
            login_page.page.locator('button:has-text("登 录")').click(force=True)
            page.wait_for_timeout(2000)

        with allure.step("验证仍在登录页"):
            assert login_page.is_logged_in() is False, "空账号不应登录成功"

        allure.attach(
            page.screenshot(),
            name="空账号截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("空密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("不填密码直接登录应失败")
    def test_login_empty_password(self, page):
        """验证空密码时登录应失败"""
        login_page = LoginPage(page)
        login_page.open()

        with allure.step("只填账号不填密码"):
            login_page.page.locator('input[placeholder="账号"]').fill(USERNAME)
            login_page.page.locator('button:has-text("登 录")').click(force=True)
            page.wait_for_timeout(2000)

        with allure.step("验证仍在登录页"):
            assert login_page.is_logged_in() is False, "空密码不应登录成功"

        allure.attach(
            page.screenshot(),
            name="空密码截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("不存在的账号")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("使用不存在的账号登录应失败")
    def test_login_nonexistent_user(self, page):
        """验证不存在的账号登录失败"""
        login_page = LoginPage(page)
        login_page.open()

        with allure.step("填写不存在的账号"):
            login_page.fill_credentials("99999999999", PASSWORD)
            login_page.submit()
            page.wait_for_timeout(3000)

        with allure.step("验证仍在登录页"):
            assert login_page.is_logged_in() is False, "不存在的账号不应登录成功"

        allure.attach(
            page.screenshot(),
            name="不存在账号截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("登录页UI验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("登录页包含账号密码输入框和登录按钮")
    def test_login_page_elements(self, page):
        """验证登录页核心元素存在"""
        login_page = LoginPage(page)
        login_page.open()

        with allure.step("验证账号输入框存在"):
            assert page.locator('input[placeholder="账号"]').count() > 0

        with allure.step("验证密码输入框存在"):
            assert page.locator('input[type="password"]').count() > 0

        with allure.step("验证登录按钮存在"):
            assert page.locator('button:has-text("登 录")').count() > 0
