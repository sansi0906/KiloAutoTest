"""
base_client.py - 基础 HTTP 客户端
==================================
封装 requests.Session，提供统一的请求方法
支持自动携带 Token 头、超时设置、会话复用
"""

import requests


class BaseClient:
    def __init__(self, base_url="", timeout=30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def set_token(self, token):
        """设置请求头中的 token，用于后续需要认证的接口"""
        self.token = token
        if token:
            self.session.headers.update({"token": token})

    def clear_token(self):
        """清除请求头中的 token"""
        self.token = None
        self.session.headers.pop("token", None)

    def request(self, method, path, **kwargs):
        """发起 HTTP 请求，自动拼接基础 URL 和超时设置"""
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, url, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        if kwargs.get("files"):
            self.session.headers.pop("Content-Type", None)
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)