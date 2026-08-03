"""
test_security.py - 安全测试
=====================================
覆盖安全场景：
- SQL 注入：在字符串字段中注入常见 SQL 注入payload
- XSS 注入：在字符串字段中注入常见 XSS payload
"""

import time

import pytest

from utils.base_test import BaseTest


@pytest.mark.security
class TestSecurity(BaseTest):
    # ==================== SQL 注入测试 ====================

    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "1' UNION SELECT NULL--",
        "admin'--",
        "' OR 'x'='x",
        "1; DELETE FROM users WHERE 1=1--",
        "' OR EXISTS(SELECT * FROM users)--",
    ])
    def test_sql_injection_user_name(self, payload):
        """在 userName 字段注入 SQL，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=payload,
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "1' UNION SELECT NULL--",
    ])
    def test_sql_injection_scope_name(self, payload):
        """在 scopeName 字段注入 SQL，应返回失败"""
        response = self.client.add_business_scope(
            scope_name=payload,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "1' UNION SELECT NULL--",
    ])
    @pytest.mark.backend_bug
    def test_sql_injection_knowledge_title(self, payload):
        """在 knowledge title 字段注入 SQL/XSS，应返回失败"""
        response = self.client.save_knowledge(
            title=payload,
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
    ])
    def test_sql_injection_service_item_name(self, payload):
        """在 itemName 字段注入 SQL，应返回失败"""
        response = self.client.add_service_item(
            item_name=payload,
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
    ])
    def test_sql_injection_company_name(self, payload):
        """在 companyName 字段注入 SQL，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.post("/platform/serverUser/save", json={
            "companyName": payload,
            "unifiedSocialCode": f"9119{int(time.time()) % 1000000000000:012d}",
            "officeAddress": [{"code": "110101000000", "name": "东城区", "level": "county"}],
            "serviceArea": [{"code": "110000000000", "name": "北京市", "level": "province"}],
            "contactPerson": "TestPerson",
            "contactPhone": "74955953457",
            "serviceItems": [1],
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "' OR 1=1 --",
    ])
    def test_sql_injection_login_username(self, payload):
        """在登录 username 字段注入 SQL，应返回失败"""
        response = self.client.login(
            username=payload,
            password="test123456",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_login_failure(data)

    # ==================== XSS 注入测试 ====================

    @pytest.mark.parametrize("payload", [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "<body onload=alert('xss')>",
        "javascript:alert('xss')",
        "<iframe src=javascript:alert('xss')>",
        "<input onfocus=alert('xss') autofocus>",
    ])
    def test_xss_user_name(self, payload):
        """在 userName 字段注入 XSS，应返回失败或净化"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=payload,
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "javascript:alert('xss')",
    ])
    def test_xss_scope_name(self, payload):
        """在 scopeName 字段注入 XSS，应返回失败或净化"""
        response = self.client.add_business_scope(
            scope_name=payload,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
    ])
    @pytest.mark.backend_bug
    def test_xss_knowledge_title(self, payload):
        """在 knowledge title 字段注入 XSS，应返回失败或净化"""
        response = self.client.save_knowledge(
            title=payload,
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "javascript:alert('xss')",
    ])
    def test_xss_item_name(self, payload):
        """在 itemName 字段注入 XSS，应返回失败或净化"""
        response = self.client.add_service_item(
            item_name=payload,
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.parametrize("payload", [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
    ])
    @pytest.mark.backend_bug
    def test_xss_content_field(self, payload):
        """在 knowledge content 字段注入 XSS，应返回失败或净化"""
        response = self.client.save_knowledge(
            title="TestTitle",
            content=payload,
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
