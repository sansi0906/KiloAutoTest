"""
token_manager.py - Token 管理工具
=================================
提供 Token 的持久化存储、读取、自动过期清理功能
Token 默认有效期 2 小时（7200 秒），过期后自动重新登录获取
支持通过轻量接口验证 Token 有效性
"""

import os
import json
import time
import requests


class TokenManager:
    def __init__(self, token_file=None, base_url=None):
        self.token_file = token_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "token.json"
        )
        self.base_url = base_url
        self.session = requests.Session()

    def save_token(self, token):
        """保存 Token 到本地文件，同时记录时间戳

        Args:
            token: JWT Token 字符串
        """
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump({"token": token, "timestamp": time.time()}, f)

    def get_token(self):
        """读取 Token，检查是否过期（2 小时有效期）

        Returns:
            Token 字符串，如果文件不存在或已过期则返回 None
        """
        if not os.path.exists(self.token_file):
            return None
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() - data.get("timestamp", 0) < 7200:
                return data.get("token")
            return None
        except (json.JSONDecodeError, OSError):
            return None

    def is_token_valid(self, token=None):
        """通过轻量接口验证 Token 是否仍然有效

        Args:
            token: 可选，不传则使用当前保存的 token

        Returns:
            bool: Token 是否有效
        """
        target_token = token or self.get_token()
        if not target_token or not self.base_url:
            return False

        try:
            resp = self.session.get(
                f"{self.base_url}/sys/getUserInfo",
                headers={"token": target_token},
                timeout=5,
            )
            data = resp.json()
            return resp.status_code == 200 and data.get("code") in ("0", "00")
        except Exception:
            return False

    def clear(self):
        """删除本地 Token 文件"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
