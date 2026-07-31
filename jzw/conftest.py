"""
津筑网App自动化测试 - 全局配置与fixture
"""
import os
import sys
import time
import pytest

# 将项目根目录加入sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from common.device_manager import DeviceManager
from common.app_helper import AppHelper


# ==================== 全局常量 ====================

PACKAGE = "com.tjxinyu.fz"
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "screenshots")
REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")

# 确保目录存在
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ==================== Session级fixture ====================

@pytest.fixture(scope="session")
def device():
    """初始化uiautomator2设备连接（整个测试会话只连接一次）"""
    dm = DeviceManager(PACKAGE)
    dm.connect()
    yield dm
    dm.cleanup()


@pytest.fixture(scope="session")
def app(device):
    """App操作助手（整个测试会话复用）"""
    helper = AppHelper(device)
    yield helper


# ==================== Function级fixture ====================

@pytest.fixture(scope="function", autouse=True)
def app_launcher(app):
    """每个测试用例前确保App在前台"""
    app.ensure_app_foreground()
    yield
    # 测试结束后回到首页，保持状态干净
    app.go_home_tab()


@pytest.fixture(scope="function")
def screenshot_on_failure(app, request):
    """测试失败时自动截图"""
    yield
    if request.node.rep_call and request.node.rep_call.failed:
        screenshot_name = f"FAIL_{request.node.name}_{int(time.time())}"
        app.screenshot(screenshot_name)


# ==================== pytest hook ====================

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """捕获测试结果用于截图判断"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
