"""
conftest.py - pytest 固件配置
===============================
定义全局固件：配置信息、Token 管理器、已登录客户端
所有测试文件自动继承这些固件
"""

import html as html_module
import json
import os
import sys
import uuid

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils.token_manager import TokenManager
from api_clients.jeecgboot_client import JeecgBootClient


_test_titles = {}


def pytest_collection_modifyitems(items):
    """将测试用例的 docstring 存储起来供报告使用，并设置为中文标题"""
    for item in items:
        doc = item.obj.__doc__
        if doc:
            title = doc.strip().split('\n')[0].strip()
            if title:
                _test_titles[item.nodeid] = title
                item.name = title


def pytest_html_report_title(report):
    """设置报告标题为中文"""
    report.title = "接口自动化测试报告"


def pytest_html_results_summary(prefix, summary, postfix, session):
    """自定义汇总区域为中文"""
    prefix.extend([
        "<h2>测试概览</h2>",
        "<p>本报告覆盖全部接口模块的自动化测试结果。</p>",
    ])


def pytest_html_results_table_header(cells):
    """在报告中增加一列 Title"""
    cells.insert(1, '<th class="sortable" data-column-type="title">测试场景</th>')


def pytest_html_results_table_row(report, cells):
    """为每行增加 Title 列，值为测试用例 docstring 第一行"""
    title = _test_titles.get(report.nodeid, "")
    escaped_title = html_module.escape(title)
    cells.insert(1, f'<td class="col-title">{escaped_title}</td>')


@pytest.fixture(scope="session")
def config():
    """返回全局配置字典，包含基础URL、登录接口、用户凭证等"""
    from config import BASE_URL, LOGIN_URL, USERNAME, PASSWORD, DB_CONFIG, DB_ENABLED, DB_CLEANUP_AFTER_TEST, DB_CLEANUP_MODULES
    return {
        "base_url": BASE_URL,
        "login_url": LOGIN_URL,
        "username": USERNAME,
        "password": PASSWORD,
        "db_config": DB_CONFIG,
        "db_enabled": DB_ENABLED,
        "db_cleanup_after_test": DB_CLEANUP_AFTER_TEST,
        "db_cleanup_modules": DB_CLEANUP_MODULES,
    }


@pytest.fixture(scope="session")
def token_manager():
    """Token 管理器固件，自动清理过期 Token 文件"""
    tm = TokenManager()
    yield tm
    tm.clear()


@pytest.fixture(scope="function")
def logged_in_client(config, token_manager):
    """已登录客户端固件，自动执行登录并携带 Token"""
    client = JeecgBootClient(base_url=config["base_url"])
    token = token_manager.get_token()
    if not token:
        response = client.login(
            username=config["username"],
            password=config["password"],
            login_type=config.get("LOGIN_TYPE", 1),
            web_type=config.get("WEB_TYPE", 0),
        )
        if response.status_code == 200:
            data = response.json()
            if data and data.get("code") in ("0", "00"):
                token = data.get("data", {}).get("token")
                token_manager.save_token(token)
    client.set_token(token)
    yield client
    client.clear_token()


@pytest.fixture(scope="session")
def execution_id():
    """生成全局执行批次ID"""
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def db_helper(config):
    """数据库工具固件（163 MySQL 测试框架数据）"""
    if not config.get("db_enabled"):
        yield None
        return
    from utils.db_helper import DatabaseHelper
    helper = DatabaseHelper(config.get("db_config"))
    yield helper


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试用例执行后自动记录结果到数据库"""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    db_helper = item.funcargs.get("db_helper")
    if not db_helper:
        return

    try:
        nodeid = item.nodeid
        parts = nodeid.split("::")
        module_path = parts[0] if len(parts) > 0 else ""
        case_name = parts[-1] if len(parts) > 2 else item.name
        module_name = module_path.replace("test_cases/", "").replace("\\", "/").split("/")[0] if module_path else "unknown"

        status = "passed" if report.passed else "failed"
        duration_ms = int(report.duration * 1000) if report.duration else None
        error_message = str(report.longrepr) if report.failed else None

        # 读取请求/响应捕获数据
        request_data = None
        response_data = None
        capture_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "requests_capture.json")
        if os.path.exists(capture_file):
            try:
                with open(capture_file, "r", encoding="utf-8") as f:
                    capture = json.load(f)
                entries = capture.get(nodeid, [])
                if entries:
                    last_entry = entries[-1]
                    request_data = json.dumps(last_entry.get("body"), ensure_ascii=False)
                    response_data = json.dumps(last_entry.get("response"), ensure_ascii=False)
            except Exception:
                pass

        module_id = db_helper.save_test_module(module_name=module_name, module_desc=module_name)
        case_id = db_helper.save_test_case(module_id=module_id, case_name=case_name, case_desc=getattr(item.obj, '__doc__', '') or "", priority="P1")
        db_helper.save_test_result(
            case_id=case_id,
            execution_id=item.funcargs.get("execution_id", ""),
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
            request_data=request_data,
            response_data=response_data,
            environment="test"
        )
    except Exception:
        pass



