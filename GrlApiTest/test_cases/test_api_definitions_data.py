"""
test_api_definitions_data.py - 数据驱动 API 定义测试
===========================================================
从 data/api_definitions.yaml 读取测试数据，参数化执行 API 定义查询测试
"""

import pytest
from api_clients.jeecgboot_client import JeecgBootClient
from utils.validator import ResponseValidator
from utils.data_driver import load_test_data


class TestApiDefinitionsDataDriven:
    @pytest.fixture(autouse=True)
    def setup(self, logged_in_client):
        """使用已登录的客户端初始化"""
        self.client = logged_in_client
        self.validator = ResponseValidator()

    @pytest.mark.parametrize(
        "test_case",
        load_test_data("data/api_definitions.yaml"),
        ids=lambda x: x["name"],
    )
    def test_api_definition_with_data(self, test_case):
        """使用数据文件中的参数执行 API 定义查询测试"""
        method = test_case.get("method", "GET").lower()
        path = test_case["path"]
        params = test_case.get("params")

        if method == "get":
            response = self.client.get(path, params=params)
        elif method == "post":
            response = self.client.post(path, json=params)
        else:
            response = self.client.request(method, path, params=params)

        self.validator.assert_status_code(response, test_case["expected_status"])