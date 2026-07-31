"""
validator.py - 响应验证工具
=============================
提供常用的 API 响应断言方法
简化测试代码中的验证逻辑
"""


class ResponseValidator:
    @staticmethod
    def assert_status_code(response, expected_code=200):
        """断言 HTTP 状态码是否符合预期

        Args:
            response: requests.Response 对象
            expected_code: 预期的状态码，默认 200

        Raises:
            AssertionError: 状态码不匹配时抛出，包含实际响应体前 500 字符
        """
        assert response.status_code == expected_code, (
            f"Expected status {expected_code}, got {response.status_code}. "
            f"Body: {response.text[:500]}"
        )

    @staticmethod
    def assert_json_key(response, key):
        """断言响应 JSON 中是否包含指定键

        Args:
            response: requests.Response 对象
            key: 需要检查的键名

        Returns:
            解析后的 JSON 数据字典

        Raises:
            AssertionError: 键不存在时抛出
        """
        data = response.json()
        assert key in data, f"Key '{key}' not found in response: {data}"
        return data

    @staticmethod
    def assert_response_time(response, max_ms=5000):
        """断言响应时间是否在允许范围内

        Args:
            response: requests.Response 对象
            max_ms: 最大允许响应时间（毫秒），默认 5000ms

        Raises:
            AssertionError: 响应时间超限时抛出
        """
        assert response.elapsed.total_seconds() * 1000 < max_ms, (
            f"Response time {response.elapsed.total_seconds() * 1000:.0f}ms "
            f"exceeds limit {max_ms}ms"
        )