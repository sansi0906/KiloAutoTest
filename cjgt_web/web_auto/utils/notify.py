# -*- coding: utf-8 -*-
"""钉钉/企微告警通知 —— 预留"""

import os


class Notifier:
    """告警通知封装，预留接口，后续按需实现"""

    def __init__(self, webhook: str = ""):
        self.webhook = os.getenv("NOTIFY_WEBHOOK", webhook)

    def send_text(self, text: str) -> bool:
        """发送文本消息（预留）"""
        if not self.webhook:
            return False
        # TODO: 实现 webhook 请求
        return True

    def send_markdown(self, title: str, content: str) -> bool:
        """发送 Markdown 消息（预留）"""
        if not self.webhook:
            return False
        # TODO: 实现 webhook 请求
        return True
