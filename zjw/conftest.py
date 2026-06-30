import pytest
import allure
import os
import datetime
from playwright.sync_api import sync_playwright


def click_and_wait_for_new_page(page, locator):
    """
    点击元素并等待新页面（新标签页或当前页面跳转）
    :param page: Playwright page 对象
    :param locator: 要点击的元素定位器
    :return: 跳转后的页面对象（可能是原页面或新标签页）
    """
    # 记录当前标签页数量
    initial_pages = page.context.pages
    
    # 点击元素
    locator.click()
    page.wait_for_load_state("networkidle")
    
    # 检查是否打开了新标签页
    if len(page.context.pages) > len(initial_pages):
        # 切换到新标签页
        new_page = page.context.pages[-1]
        new_page.wait_for_load_state("networkidle")
        return new_page
    else:
        # 在当前页面跳转
        return page


# 报告目录配置
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

# 从环境变量获取截图目录，如果没有设置则使用默认目录
SCREENSHOTS_DIR = os.environ.get("SCREENSHOT_DIR", os.path.join(REPORTS_DIR, "screenshots"))
ALLURE_RESULTS_DIR = os.path.join(REPORTS_DIR, "allure-results")

# 确保目录存在
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
# 默认测试地址（只需修改这一处，或通过命令行参数覆盖）
DEFAULT_TEST_URL = "http://dev.tj.gongrenle.com/"

# 浏览器配置
BROWSER_CONFIG = {
    "slow_mo": 500,           # 操作延迟（毫秒）
    "headless": False          # 是否无头模式
}

# 测试环境信息
TEST_ENV = {
    "测试环境": "开发环境",
    "测试地址": DEFAULT_TEST_URL,  # 使用变量引用
    "浏览器": "Chromium",
    "操作系统": os.name,
    "测试人员": "",
    "备注": ""
}

# 全局配置
SCREENSHOT_ON_FAILURE = True  # 失败时截图
SCREENSHOT_ON_PASS = False    # 通过时截图


def pytest_addoption(parser):
    """添加自定义命令行参数"""
    parser.addoption("--tester", action="store", default="", help="测试人员姓名")
    parser.addoption("--remark", action="store", default="", help="测试备注信息")
    parser.addoption("--screenshot-all", action="store_true", default=False, 
                     help="对所有测试截图（包括通过的测试）")
    parser.addoption("--viewport-width", type=int, default=1920, help="浏览器视口宽度，默认1920")
    parser.addoption("--viewport-height", type=int, default=1080, help="浏览器视口高度，默认1080")
    parser.addoption("--test-url", action="store", default=DEFAULT_TEST_URL, 
                     help=f"测试地址，默认: {DEFAULT_TEST_URL}")


def pytest_configure(config):
    """pytest 配置初始化"""
    TEST_ENV["测试人员"] = config.getoption("--tester") or "未指定"
    TEST_ENV["备注"] = config.getoption("--remark") or "无"
    
    # 更新测试地址（从命令行参数或默认值）
    TEST_ENV["测试地址"] = config.getoption("--test-url")
    
    # 设置是否对所有测试截图
    global SCREENSHOT_ON_PASS
    SCREENSHOT_ON_PASS = config.getoption("--screenshot-all")
    
    # 设置 Allure 结果目录
    config.option.allure_report_dir = ALLURE_RESULTS_DIR
    
    # 从环境变量获取截图目录（动态更新）
    global SCREENSHOTS_DIR
    env_screenshot_dir = os.environ.get("SCREENSHOT_DIR")
    if env_screenshot_dir:
        SCREENSHOTS_DIR = env_screenshot_dir
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    # 写入环境信息到 Allure
    env_file = os.path.join(ALLURE_RESULTS_DIR, "environment.properties")
    with open(env_file, "w", encoding="utf-8") as f:
        for key, value in TEST_ENV.items():
            f.write(f"{key}={value}\n")


# 测试文件执行顺序（按模块优先级排序）
TEST_ORDER = [
    "test_page_structure.py",       # 页面结构测试（基础）
    "test_key_projects.py",         # 重点项目测试
    "test_industry_news.py",        # 行业新闻测试
    "test_supply_chain_map.py",     # 供应链地图测试
    "test_industry_demand.py",      # 行业需求测试
    "test_all_products.py",         # 全部产品测试
    "test_supply_hall.py",          # 供应大厅测试
    "test_interaction_performance.py",  # 交互性能测试
    "test_industrial_service.py",   # 工业服务测试
]

def pytest_collection_modifyitems(items):
    """自定义测试用例执行顺序"""
    def get_order(item):
        """获取测试文件的优先级"""
        filename = os.path.basename(item.location[0])
        if filename in TEST_ORDER:
            return TEST_ORDER.index(filename)
        return len(TEST_ORDER)
    
    # 按优先级排序
    items.sort(key=get_order)


@pytest.fixture(scope="session")
def browser():
    """浏览器 fixture - 使用配置中的参数"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=BROWSER_CONFIG["headless"], 
            slow_mo=BROWSER_CONFIG["slow_mo"]
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, request):
    # 从命令行参数获取视口尺寸
    viewport_width = request.config.getoption("--viewport-width")
    viewport_height = request.config.getoption("--viewport-height")
    # 从命令行参数获取测试地址
    base_url = request.config.getoption("--test-url")
    
    page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
    page.goto(base_url)
    
    # 使用更宽松的等待策略：先等待DOMContentLoaded，再尝试networkidle
    try:
        page.wait_for_load_state("domcontentloaded")
        # 尝试等待networkidle，如果超时则跳过
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        # networkidle超时不影响测试继续执行
        pass
    
    # 将 page 对象存储到 request 中，供钩子使用
    request.node.page = page
    
    yield page
    
    page.close()


def _take_screenshot(page, item, status: str) -> str:
    """
    截取测试截图
    :param page: Playwright page 对象
    :param item: 测试用例对象
    :param status: 测试状态 (passed/failed)
    :return: 截图路径
    """
    try:
        # 生成截图文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = item.name.replace("::", "_").replace(".", "_")
        screenshot_name_prefix = "通过" if status == "passed" else "失败"
        screenshot_name = f"{screenshot_name_prefix}_{test_name}_{timestamp}.png"
        screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)
        
        # 检查是否有新打开的标签页
        screenshot_page = page.context.pages[-1] if len(page.context.pages) > 1 else page
        
        # 截图
        screenshot_page.screenshot(path=screenshot_path, full_page=True)
        
        # 将截图附加到 Allure 报告
        with open(screenshot_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"{screenshot_name_prefix}截图",
                attachment_type=allure.attachment_type.PNG
            )
        
        return screenshot_path
    except Exception as e:
        print(f"截图失败: {e}")
        return ""


@ pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试执行后生成报告的钩子"""
    outcome = yield
    report = outcome.get_result()
    
    # 只在 call 阶段处理
    if report.when == "call":
        # 获取 page 对象
        page = getattr(item, "page", None)
        
        if page:
            # 判断是否需要截图
            if report.failed and SCREENSHOT_ON_FAILURE:
                report.extra_screenshot = _take_screenshot(page, item, "failed")
            elif report.passed and SCREENSHOT_ON_PASS:
                report.extra_screenshot = _take_screenshot(page, item, "passed")
        
        # 附加测试执行时间
        duration = call.duration if hasattr(call, "duration") else 0
        allure.attach(
            f"{duration:.2f}秒",
            name="执行时长",
            attachment_type=allure.attachment_type.TEXT
        )


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """测试开始前的钩子，记录测试模块信息"""
    module_name = item.module.__name__ if hasattr(item, "module") else "未知模块"
    allure.dynamic.feature(module_name.replace("test_", "").replace("_", " ").title())
    
    # 获取测试方法的文档字符串作为描述
    if hasattr(item, "function") and item.function.__doc__:
        allure.dynamic.description(item.function.__doc__)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """测试结束后的汇总信息"""
    print("\n" + "=" * 60)
    print("测试报告已生成")
    print(f"截图目录: {SCREENSHOTS_DIR}")
    print(f"Allure结果: {ALLURE_RESULTS_DIR}")
    if SCREENSHOT_ON_PASS:
        print("截图模式: 全部测试截图")
    else:
        print("截图模式: 仅失败测试截图")
    print("=" * 60)
