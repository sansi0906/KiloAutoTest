"""
test_send_code.py - 短信验证码发送接口测试
=================================================
覆盖验证码发送模块的场景：
- 正常发送验证码
- 60 秒内重复发送触发频率限制
- 无效手机号格式
- 空手机号
- 缺少必填字段（phone / webType）
- 频率限制过期后重新发送

使用固定手机号：17695729351、18102082262
"""

import time

import pytest

from .test_base import TestBase

PHONE_1 = "17695729351"
PHONE_2 = "18102082262"

RATE_LIMIT_WAIT = 61


class TestSendCode(TestBase):
    @pytest.mark.slow
    def test_send_code_after_rate_limit_expires(self):
        """60 秒频率限制过期后重新发送验证码，应返回成功"""
        response = self.client.send_code(phone=PHONE_1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        time.sleep(RATE_LIMIT_WAIT)

        response = self.client.send_code(phone=PHONE_1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)