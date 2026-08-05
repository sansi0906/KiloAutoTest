# -*- coding: utf-8 -*-
"""登录页面对象"""
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import logger


class LoginPage(BasePage):
    """登录页面"""

    # 选择器
    USERNAME_INPUT = 'input[placeholder="账号"]'
    PASSWORD_INPUT = 'input[type="password"]'
    LOGIN_BUTTON = 'button:has-text("登 录")'

    def __init__(self, page: Page):
        super().__init__(page)

    def open(self) -> None:
        """打开登录页"""
        from config.env_config import BASE_URL
        self.page.goto(f"{BASE_URL}/adminLogin")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(3000)
        logger.info("打开登录页")

    def fill_credentials(self, username: str, password: str) -> None:
        """填写用户名和密码（使用 fill 触发 React 状态更新）"""
        self.page.locator(self.USERNAME_INPUT).fill(username)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        logger.info(f"填写用户名: {username}")

    def submit(self) -> None:
        """点击登录按钮提交"""
        self.page.locator(self.LOGIN_BUTTON).first.click(force=True)
        logger.info("点击登录按钮")

    def is_logged_in(self) -> bool:
        """检查是否已登录（URL 不再包含 login / adminLogin）"""
        url = self.page.url.lower()
        return "login" not in url and "adminlogin" not in url

    def wait_for_login_success(self, timeout_ms: int = 15000) -> bool:
        """
        等待登录成功 —— 轮询检查 URL 变化（SPA 路由跳转不触发 navigation 事件）

        Returns:
            是否登录成功
        """
        interval = 500
        elapsed = 0
        while elapsed < timeout_ms:
            self.page.wait_for_timeout(interval)
            elapsed += interval
            if self.is_logged_in():
                # 等待首页加载完成
                self.page.wait_for_timeout(3000)
                logger.info(f"登录成功，跳转到: {self.page.url}")
                return True

        # 最终检查
        if self.is_logged_in():
            logger.info(f"登录成功，跳转到: {self.page.url}")
            return True

        # 收集错误提示
        errors = self.page.evaluate("""
            () => {
                const els = document.querySelectorAll(
                    '.ant-message-error, .ant-form-item-explain, .ant-notification-notice-message'
                );
                return Array.from(els)
                    .filter(e => e.offsetParent !== null)
                    .map(e => e.textContent.trim());
            }
        """)
        logger.error(f"登录失败，URL={self.page.url}, 错误={errors}")
        return False

    def login(self, username: str, password: str) -> bool:
        """
        完整登录流程：打开 -> 填写 -> 提交 -> 等待跳转

        Returns:
            是否登录成功
        """
        # 等待表单渲染完成
        self.page.wait_for_selector(self.USERNAME_INPUT, timeout=10000)
        self.page.wait_for_timeout(500)

        self.fill_credentials(username, password)
        self.page.wait_for_timeout(500)

        # 等待登录按钮就绪
        self.page.wait_for_selector(self.LOGIN_BUTTON, timeout=5000)
        self.submit()

        return self.wait_for_login_success()
