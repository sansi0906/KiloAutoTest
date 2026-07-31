"""
test_token_expiration.py - Token 过期与并发有效性测试
======================================================
覆盖 Token 相关场景：
- 使用有效 Token 访问接口
- 使用过期 Token 访问接口
- Token 并发有效性
"""

import threading
import time

import pytest

from api_clients.jeecgboot_client import JeecgBootClient

from utils.base_test import BaseTest


class TestTokenExpiration(BaseTest):
    def test_valid_token_access(self):
        """使用有效 Token 访问接口，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_expired_token_access(self):
        """使用过期 Token 访问接口，应返回失败"""
        self.client.set_token("expired_token_12345")

        response = self.client.page_users(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_concurrent_token_validity(self):
        """多个线程使用同一 Token 并发访问，应全部成功"""
        token = self.login()
        results = []
        errors = []

        def make_request():
            try:
                client = JeecgBootClient(base_url=self.config["base_url"])
                client.set_token(token)
                response = client.page_users(page_num=1, page_size=10)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = []
        for _ in range(3):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert all(code == 200 for code in results)
