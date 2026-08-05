# -*- coding: utf-8 -*-
"""
pytest 全局 fixture —— 核心配置

提供 browser / context / page / logged_in_page 等fixture

优化点：
  - browser: session 级别，整轮测试只启动一次浏览器
  - logged_in_context: module 级别，每个测试文件只登录一次
  - logged_in_page: function 级别，用新 page 共享已登录 context，无需重新登录
"""
import os
import sys
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.env_config import (
    BASE_URL, USERNAME, PASSWORD, HEADLESS, BROWSER,
    VIEWPORT_WIDTH, VIEWPORT_HEIGHT, PROXY, TIMEOUT,
)
from pages.login_page import LoginPage
from utils.logger import logger


# ──────────── 浏览器 fixture ────────────

@pytest.fixture(scope="session")
def playwright_instance():
    """启动 Playwright（session 级别，整轮测试只启动一次）"""
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """启动浏览器（session 级别）"""
    launch_kwargs = {"headless": HEADLESS}
    if PROXY:
        launch_kwargs["proxy"] = {"server": PROXY}

    if BROWSER == "firefox":
        br = playwright_instance.firefox.launch(**launch_kwargs)
    elif BROWSER == "webkit":
        br = playwright_instance.webkit.launch(**launch_kwargs)
    else:
        br = playwright_instance.chromium.launch(**launch_kwargs)

    yield br
    br.close()


# ──────────── 未登录 fixture（登录测试用）────────────

@pytest.fixture(scope="function")
def context(browser):
    """创建浏览器上下文（每个测试函数独立，用于未登录场景）"""
    ctx = browser.new_context(
        viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
        ignore_https_errors=True,
    )
    ctx.set_default_timeout(TIMEOUT)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    """创建新页面（未登录，用于登录测试等）"""
    pg = context.new_page()
    yield pg
    pg.close()


# ──────────── 已登录 fixture（业务/UI 测试用）────────────

@pytest.fixture(scope="module")
def logged_in_context(browser):
    """
    module 级别已登录 context —— 每个测试文件只登录一次
    context 保存 cookies + localStorage + sessionStorage，完整保持登录状态
    """
    ctx = browser.new_context(
        viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
        ignore_https_errors=True,
    )
    ctx.set_default_timeout(TIMEOUT)

    # 用临时 page 执行登录
    pg = ctx.new_page()
    login_page = LoginPage(pg)
    login_page.open()
    assert login_page.login(USERNAME, PASSWORD), "module 登录失败"
    logger.info(f"module 级登录成功 (文件级共享)")
    pg.close()  # 关闭登录页，但 context 保留了登录状态

    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def logged_in_page(logged_in_context):
    """
    已登录的 page —— 业务测试和 UI 测试使用此 fixture

    优化：复用 module 级别的 logged_in_context，无需重新登录
    每个测试有独立的 page（状态隔离，互不影响）
    """
    pg = logged_in_context.new_page()
    yield pg
    pg.close()


# ──────────── 测试数据 fixture ────────────

@pytest.fixture(scope="function")
def test_data():
    """加载 YAML 测试数据，自动填充时间戳"""
    import yaml
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "test_data.yaml"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    ts = datetime.now().strftime("%H%M%S")

    # 递归替换 {ts} 占位符
    def fill_ts(obj):
        if isinstance(obj, str):
            return obj.replace("{ts}", ts)
        if isinstance(obj, dict):
            return {k: fill_ts(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [fill_ts(i) for i in obj]
        return obj

    return fill_ts(raw)
