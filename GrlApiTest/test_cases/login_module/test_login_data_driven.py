"""
test_login_data_driven.py - 数据驱动登录测试
==================================================
从 data/login_data.json 读取测试数据，参数化执行登录测试
"""

import pytest
from utils.base_test import BaseTest
from utils.data_driver import load_test_data


class TestLoginDataDriven(BaseTest):
    @pytest.mark.parametrize(
        "test_case",
        load_test_data("data/login_data.json"),
        ids=lambda x: x["name"],
    )
    def test_login_with_data(self, test_case):
        """使用数据文件中的参数执行登录测试"""
        response = self.client.login(
            username=test_case["username"],
            password=test_case["password"],
            login_type=self.config.get("LOGIN_TYPE", 1),
            web_type=self.config.get("WEB_TYPE", 0),
        )
        self.validator.assert_status_code(response, test_case["expected_status"])
        data = response.json()
        if test_case["name"] == "test_login_success":
            self.assert_login_success(data)
        else:
            self.assert_login_failure(data)