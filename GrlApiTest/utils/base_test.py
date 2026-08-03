"""
base_test.py - 通用测试基类
=============================
所有模块测试类的基类，提供通用的 setup、login、断言、数据库记录等功能。
各模块只需实现特有的工厂方法。
"""

import time
import uuid
import random

import pytest

from api_clients.jeecgboot_client import JeecgBootClient
from utils.validator import ResponseValidator


class BaseTest:
    @pytest.fixture(autouse=True)
    def setup(self, config, execution_id, db_helper, pg_cleanup, request):
        """自动初始化客户端、验证器并登录"""
        self.client = JeecgBootClient(base_url=config["base_url"])
        self.validator = ResponseValidator()
        self.config = config
        self.execution_id = execution_id
        self.db_helper = db_helper
        self.pg_cleanup = pg_cleanup
        self._created_ids = []
        self._module_id = None
        self._test_name = request.node.name
        token = self.login()
        self.client.set_token(token)

    def teardown_method(self):
        """清理测试创建的接口数据"""
        for item_id in getattr(self, "_created_ids", []):
            try:
                self._delete_test_data(item_id)
            except Exception as e:
                if self.db_helper:
                    try:
                        self.db_helper.save_test_log(
                            execution_id=self.execution_id,
                            level="WARNING",
                            message=f"Failed to cleanup test data id={item_id}: {e}",
                            module=getattr(self, '_module_name', 'unknown'),
                            case_name=getattr(self, '_test_name', 'unknown'),
                        )
                    except Exception:
                        pass

    def _log_test_data_created(self, item_id, item_name=None):
        """记录测试数据创建日志"""
        if self.db_helper:
            try:
                self.db_helper.save_test_log(
                    execution_id=self.execution_id,
                    level="INFO",
                    message=f"Test data created: id={item_id}, name={item_name}",
                    module=getattr(self, '_module_name', 'unknown'),
                    case_name=getattr(self, '_test_name', 'unknown'),
                )
            except Exception:
                pass

    def _delete_test_data(self, item_id):
        """删除测试数据，由子类实现具体删除逻辑"""
        pass

    def login(self, username=None, password=None, login_type=None, web_type=None):
        """执行登录并返回 Token"""
        response = self.client.login(
            username=username or self.config["username"],
            password=password or self.config["password"],
            login_type=login_type or self.config.get("LOGIN_TYPE", 1),
            web_type=web_type or self.config.get("WEB_TYPE", 0),
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Login failed: {data}"
        return data.get("data", {}).get("token")

    def assert_login_success(self, data):
        """断言登录成功"""
        assert data.get("code") in ("0", "00"), f"Login failed: {data}"
        assert data.get("data", {}).get("token"), "Token is missing in response"

    def assert_login_failure(self, data):
        """断言登录失败"""
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def assert_save_success(self, data, message=None):
        """断言操作成功"""
        assert data.get("code") in ("0", "00"), f"Operation failed: {data}"
        if message:
            assert data.get("message") == message, f"Unexpected message: {data.get('message')}"

    def assert_response_time(self, response, max_duration_ms=500):
        """断言接口响应时间不超过阈值"""
        duration_ms = response.elapsed.total_seconds() * 1000
        assert duration_ms <= max_duration_ms, \
            f"Response too slow: {duration_ms:.0f}ms > {max_duration_ms}ms"
        return duration_ms

    def assert_save_failure(self, data, expected_code=None):
        """断言操作失败"""
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"
        if expected_code:
            assert data.get("code") == expected_code, f"Expected code {expected_code}, got: {data.get('code')}"

    def _get_module_id(self, module_name, module_desc=""):
        """获取或创建模块ID"""
        if self._module_id is None and self.db_helper:
            self._module_id = self.db_helper.save_test_module(module_name, module_desc)
        return self._module_id

    def _save_test_result(self, case_name, status, duration_ms=None, error_message=None,
                          request_data=None, response_data=None, assertion_details=None, module_name=None, module_desc=""):
        """保存测试结果到数据库（163 MySQL）"""
        if not self.db_helper:
            return
        module_id = self._get_module_id(module_name or self._module_name, module_desc)
        if not module_id:
            return
        case_id = self.db_helper.save_test_case(
            module_id=module_id,
            case_name=case_name,
            case_desc="",
            priority="P1"
        )
        self.db_helper.save_test_result(
            case_id=case_id,
            execution_id=self.execution_id,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
            request_data=request_data,
            response_data=response_data,
            assertion_details=assertion_details,
            environment="test"
        )

    def _record_test_result(self, case_name, response, start_time=None, module_name=None, module_desc=""):
        """记录测试结果，自动判断成功/失败"""
        import time
        duration_ms = int((time.time() - start_time) * 1000) if start_time else None
        data = response.json() if response.status_code == 200 else {}
        status = "passed" if data.get("code") in ("0", "00") else "failed"
        self._save_test_result(
            case_name=case_name,
            status=status,
            duration_ms=duration_ms,
            error_message=data.get("message") if status == "failed" else None,
            response_data=str(data),
            module_name=module_name,
            module_desc=module_desc
        )

    def _unique_real_name(self):
        """生成唯一的真实姓名"""
        return f"测试用户{int(time.time())}"

    def _unique_user_name(self):
        """生成唯一的用户名（174开头的11位手机号）"""
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    def _get_existing_service_item(self, display_only=True):
        """获取一个已存在的服务项目"""
        if display_only:
            resp = self.client.list_display_service_items(is_display=1)
        else:
            resp = self.client.list_display_service_items()
        self.validator.assert_status_code(resp, 200)
        data = resp.json()
        self.assert_save_success(data)
        items = data.get("data", [])
        assert items, "No service items found"
        return items[0]["id"], items[0]["itemName"]
