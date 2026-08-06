"""
超级个体后台管理系统 - 测试基础配置
提供登录、页面导航等公共方法
"""
import asyncio
import os
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# 页面路由
PAGES = {
    "服务项目配置": "/smart-service/project-config",
    "服务定价配置": "/smart-service/project-price",
    "合同服务配置": "/smart-service/contract-service",
    "经营范围配置": "/smart-service/scope-config",
    "知识库": "/content-manage/knowledge",
}


class TestBase:
    """测试基类，提供公共方法"""

    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.test_results = []
        self.current_module = ""

    async def setup(self, headless=False):
        """初始化浏览器"""
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()

    async def teardown(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.pw:
            await self.pw.stop()

    async def login(self):
        """登录系统"""
        await self.page.goto(LOGIN_URL, wait_until="networkidle")
        await self.page.wait_for_timeout(2000)
        await self.page.fill('input[placeholder="账号"]', USERNAME)
        await self.page.fill('input[type="password"]', PASSWORD)
        await self.page.click('button:has-text("登 录")')
        await self.page.wait_for_timeout(3000)
        assert "/dashboard" in self.page.url, f"登录失败，当前URL: {self.page.url}"

    async def navigate_to(self, page_name):
        """导航到指定页面"""
        path = PAGES.get(page_name)
        assert path, f"未知页面: {page_name}"
        url = f"{BASE_URL}{path}"
        await self.page.goto(url, wait_until="networkidle")
        await self.page.wait_for_timeout(2000)

    def record_result(self, test_name, passed, expected="", actual="", screenshot=""):
        """记录测试结果"""
        result = {
            "module": self.current_module,
            "test_name": test_name,
            "passed": passed,
            "expected": expected,
            "actual": actual,
            "screenshot": screenshot,
        }
        self.test_results.append(result)
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")
        if not passed:
            print(f"    预期: {expected}")
            print(f"    实际: {actual}")

    async def screenshot(self, name):
        """截图"""
        path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
        await self.page.screenshot(path=path)
        return path

    async def get_table_headers(self):
        """获取表格列头"""
        return await self.page.evaluate("""
            () => {
                const ths = document.querySelectorAll('th, .ant-table-thead th');
                const texts = [];
                for (const th of ths) {
                    const text = th.textContent.trim();
                    if (text) texts.push(text);
                }
                return texts;
            }
        """)

    async def get_table_row_count(self):
        """获取表格数据行数"""
        return await self.page.evaluate("""
            () => {
                const rows = document.querySelectorAll('.ant-table-tbody tr');
                return rows.length;
            }
        """)

    async def get_buttons(self):
        """获取页面所有按钮文本"""
        return await self.page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button, .ant-btn');
                const texts = [];
                for (const btn of buttons) {
                    const text = btn.textContent.trim();
                    if (text && text.length < 30) texts.push(text);
                }
                return [...new Set(texts)];
            }
        """)

    async def click_button(self, text):
        """点击包含指定文本的按钮"""
        btn = self.page.locator(f'button:has-text("{text}"), .ant-btn:has-text("{text}")').first
        if await btn.count() > 0:
            await btn.click()
            await self.page.wait_for_timeout(1000)
            return True
        return False

    async def fill_input(self, placeholder, value):
        """填写输入框"""
        inp = self.page.locator(f'input[placeholder="{placeholder}"]').first
        if await inp.count() > 0:
            await inp.fill(value)
            return True
        return False

    async def has_text(self, text):
        """检查页面是否包含指定文本"""
        locator = self.page.locator(f'text="{text}"')
        return await locator.count() > 0

    async def wait_for_modal(self):
        """等待弹窗/抽屉出现"""
        await self.page.wait_for_timeout(1000)
        modal = self.page.locator('.ant-modal, .ant-drawer-content').first
        return await modal.count() > 0

    async def close_modal(self):
        """关闭弹窗"""
        close_btn = self.page.locator('.ant-modal-close, .ant-drawer-close').first
        if await close_btn.count() > 0:
            await close_btn.click()
            await self.page.wait_for_timeout(500)

    async def get_form_errors(self):
        """获取表单错误提示（修复版：支持多种选择器）"""
        # 先等待验证错误显示
        await self.page.wait_for_timeout(500)
        return await self.page.evaluate("""
            () => {
                const errors = [];
                
                // 方法1: .ant-form-item-explain-error (Ant Design标准类)
                const errorElements = document.querySelectorAll('.ant-form-item-explain-error');
                for (const el of errorElements) {
                    const text = el.textContent.trim();
                    if (text) errors.push(text);
                }
                
                // 方法2: 检查class包含error的元素
                const allElements = document.querySelectorAll('[class*="error"]');
                for (const el of allElements) {
                    const text = el.textContent.trim();
                    if (text && text.includes('请输入')) {
                        errors.push(text);
                    }
                }
                
                return [...new Set(errors)];
            }
        """)
