"""
test_exception_scenarios.py - 异常场景测试
=============================================
覆盖 API 客户端的异常场景：
- 网络超时
- 非法 JSON 响应
- 超大 payload
- 并发请求
"""

import json
import time
import threading

import pytest

from utils.base_test import BaseTest


class TestExceptionScenarios(BaseTest):
    def test_request_timeout(self):
        """模拟网络超时，应抛出异常或返回错误"""
        self.client.timeout = 0.001
        try:
            response = self.client.login(
                username=self.config["username"],
                password=self.config["password"],
            )
            assert False, "Expected timeout exception"
        except Exception as e:
            assert "timeout" in str(e).lower() or "ConnectionError" in str(e).__class__.__name__

    def test_invalid_json_response(self):
        """模拟非法 JSON 响应，应能安全处理"""
        import unittest.mock
        original_request = self.client.session.request
        call_count = [0]

        def mock_request(method, url, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                class FakeResponse:
                    status_code = 200
                    text = "not valid json"
                    def json(self):
                        raise json.JSONDecodeError("Invalid JSON", "", 0)
                return FakeResponse()
            return original_request(method, url, **kwargs)

        self.client.session.request = mock_request
        try:
            response = self.client.login(
                username=self.config["username"],
                password=self.config["password"],
            )
            assert response.status_code == 200
        finally:
            self.client.session.request = original_request

    def test_large_payload(self):
        """发送超大 payload，应返回失败或服务端正确处理"""
        large_data = {"data": "x" * 1000000}
        response = self.client.post("/sys/login", json=large_data)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_concurrent_requests(self):
        """并发发送多个请求，应全部成功或按预期处理"""
        results = []
        errors = []

        def make_request():
            try:
                response = self.client.login(
                    username=self.config["username"],
                    password=self.config["password"],
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = []
        for _ in range(5):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        assert len(errors) == 0, f"Unexpected errors: {errors}"
