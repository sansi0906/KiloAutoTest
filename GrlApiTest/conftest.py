"""
conftest.py - pytest 固件配置
===============================
定义全局固件：配置信息、Token 管理器、已登录客户端
所有测试文件自动继承这些固件
"""

import html as html_module
import os
import random
import sys
import time
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
    from config import BASE_URL, LOGIN_URL, USERNAME, PASSWORD, DB_CONFIG, DB_ENABLED, DB_CLEANUP_AFTER_TEST, DB_CLEANUP_MODULES, PG_CONFIG, PG_CLEANUP_UUID, PG_CLEANUP_ENABLED, LOGIN_TYPE, WEB_TYPE
    return {
        "base_url": BASE_URL,
        "login_url": LOGIN_URL,
        "username": USERNAME,
        "password": PASSWORD,
        "login_type": LOGIN_TYPE,
        "web_type": WEB_TYPE,
        "db_config": DB_CONFIG,
        "db_enabled": DB_ENABLED,
        "db_cleanup_after_test": DB_CLEANUP_AFTER_TEST,
        "db_cleanup_modules": DB_CLEANUP_MODULES,
        "pg_config": PG_CONFIG,
        "pg_cleanup_uuid": PG_CLEANUP_UUID,
        "pg_cleanup_enabled": PG_CLEANUP_ENABLED,
    }


@pytest.fixture(scope="session")
def token_manager(config):
    """Token 管理器固件，自动清理过期 Token 文件"""
    tm = TokenManager(base_url=config["base_url"])
    yield tm
    tm.clear()


@pytest.fixture(scope="function")
def logged_in_client(config, token_manager):
    """已登录客户端固件，自动执行登录并携带 Token"""
    client = JeecgBootClient(base_url=config["base_url"])
    token = token_manager.get_token()
    if not token or not token_manager.is_token_valid(token):
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


@pytest.fixture(scope="session", autouse=True)
def ensure_test_data(config, token_manager):
    """Session 级数据预置：确保测试环境有基础依赖数据"""
    client = JeecgBootClient(base_url=config["base_url"])
    token = token_manager.get_token()
    if not token or not token_manager.is_token_valid(token):
        response = client.login(
            username=config["username"],
            password=config["password"],
            login_type=config.get("login_type", 1),
            web_type=config.get("web_type", 0),
        )
        if response.status_code == 200:
            data = response.json()
            if data and data.get("code") in ("0", "00"):
                token = data.get("data", {}).get("token")
                token_manager.save_token(token)
    if not token:
        import logging
        logging.warning("ensure_test_data: 无法获取有效 token，跳过数据预置")
        yield
        return
    client.set_token(token)

    try:
        _ensure_service_items(client, min_count=3)
        _ensure_business_scope(client)
        _ensure_role(client)
        _ensure_service_provider_role(client)
    except Exception as e:
        import logging
        logging.warning(f"ensure_test_data 预置失败: {e}")

    yield
    client.clear_token()


def _ensure_service_items(client, min_count=3):
    """确保至少有 min_count 个展示的服务项目"""
    for _ in range(min_count):
        resp = client.page_service_items(page_num=1, page_size=100, is_display=1)
        if resp.status_code == 200:
            data = resp.json()
            records = data.get("data", {}).get("records", [])
            if len(records) >= min_count:
                return
        client.add_service_item(
            item_name=f"AutoItem{int(time.time())}_{random.randint(1000, 9999)}",
            billing_method=1,
            subtitle="AutoSubtitle",
            item_desc="AutoDescription",
        )


def _ensure_business_scope(client):
    """确保至少有 1 个启用的经营范围"""
    resp = client.page_business_scopes(page_num=1, page_size=10, is_enabled=1)
    if resp.status_code == 200:
        data = resp.json()
        records = data.get("data", {}).get("records", [])
        if records:
            return
    client.add_business_scope(
        scope_name=f"AutoScope{int(time.time())}",
        remark="AutoRemark",
    )


def _ensure_role(client):
    """确保至少有 1 个启用的角色，且存在服务商角色 SP1001"""
    resp = client.page_roles(page_num=1, page_size=10, status=1)
    if resp.status_code == 200:
        data = resp.json()
        records = data.get("data", {}).get("records", [])
        if records:
            return
    client.save_role(
        role_name=f"AutoRole{int(time.time())}",
        status=1,
        role_remark="AutoRemark",
    )


def _ensure_service_provider_role(client):
    """确保服务商角色 SP1001 存在（系统预设角色，API 不允许创建，直接插入数据库）"""
    from config import PG_CONFIG
    from utils.db_helper import DatabaseHelper
    pg_helper = DatabaseHelper(PG_CONFIG)

    role = pg_helper.fetch_one(
        "SELECT id FROM cjgt_platform_role WHERE role_no = %s AND delete_status = 0",
        ("SP1001",)
    )
    if role:
        return role["id"]

    role_id = pg_helper.execute(
        """INSERT INTO cjgt_platform_role 
           (role_name, role_remark, status, create_user_name, last_modify_name, delete_status, create_user_uuid, last_modify_uuid, role_no, web_type) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ("服务商", "系统预设服务商角色", 1, "system", "system", 0, "00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000", "SP1001", 0)
    )
    return role_id


@pytest.fixture(scope="session")
def db_helper(config, execution_id):
    """数据库工具固件（163 MySQL 测试框架数据）"""
    if not config.get("db_enabled"):
        yield None
        return
    from utils.db_helper import DatabaseHelper
    helper = DatabaseHelper(config.get("db_config"))
    yield helper
    if config.get("db_cleanup_after_test"):
        try:
            helper.cleanup_test_data(execution_id=execution_id)
        except Exception as e:
            import logging
            logging.warning(f"MySQL test data cleanup failed: {e}")


@pytest.fixture(scope="session")
def pg_helper(config):
    """PostgreSQL 工具固件（165 业务数据库）"""
    pg_config = config.get("pg_config")
    if not pg_config:
        yield None
        return
    from utils.db_helper import DatabaseHelper
    helper = DatabaseHelper(pg_config)
    yield helper


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试用例执行后自动记录结果到数据库，失败时附加 Allure 日志"""
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

        request_data = None
        response_data = None
        instance = getattr(item, "instance", None)
        client = getattr(instance, "client", None) if instance else None
        history = getattr(client, "_request_history", None) if client else None

        if history:
            last_entry = history[-1] if history else None
            if last_entry:
                import json
                request_data = json.dumps(last_entry.get("body"), ensure_ascii=False)
                response_data = json.dumps(last_entry.get("response"), ensure_ascii=False)

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

        if report.failed:
            try:
                import allure
                allure.attach(
                    error_message or "Test failed without detailed error",
                    name="Error Details",
                    attachment_type=allure.attachment_type.TEXT,
                )
                if request_data:
                    allure.attach(
                        request_data,
                        name="Last Request Body",
                        attachment_type=allure.attachment_type.TEXT,
                    )
                if response_data:
                    allure.attach(
                        response_data,
                        name="Last Response Body",
                        attachment_type=allure.attachment_type.TEXT,
                    )
            except Exception:
                pass
    except Exception as e:
        import logging
        logging.warning(f"Failed to record test result for {item.nodeid}: {e}")


@pytest.fixture(scope="session")
def pg_cleanup(config):
    """PostgreSQL 业务数据清理固件（165 业务数据）"""
    if not config.get("pg_cleanup_enabled"):
        yield None
        return
    from utils.pg_cleanup import cleanup_test_data
    yield cleanup_test_data
    try:
        cleanup_test_data(creator_uuid=config.get("pg_cleanup_uuid"), dry_run=False)
    except Exception as e:
        import logging
        logging.warning(f"PostgreSQL cleanup failed: {e}")
