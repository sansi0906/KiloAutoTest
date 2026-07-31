"""
token_manager.py - Token 管理工具
==================================
提供 Token 的持久化存储、读取、自动过期清理功能
Token 默认有效期 2 小时（7200 秒），过期后自动重新登录获取
"""

import os
import json
import time


class TokenManager:
    def __init__(self, token_file=None):
        self.token_file = token_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "token.json"
        )

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

    def clear(self):
        """删除本地 Token 文件"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)