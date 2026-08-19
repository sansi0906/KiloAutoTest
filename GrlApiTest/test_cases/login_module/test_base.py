"""
test_base.py - 登录模块测试基类
==================================================
提供登录模块的通用测试设置和辅助方法
"""

import time

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "login_module"
    _module_desc = "登录模块"

    def _get_sms_code_from_db(self, phone, pg_helper=None):
        """从 PostgreSQL 数据库查询最新的短信验证码

        Args:
            phone: 手机号
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            str: 验证码，如果未找到则返回 None
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT code FROM cjgt_sms_log
            WHERE phone = %s
            ORDER BY send_time DESC
            LIMIT 1
        """
        try:
            result = pg_helper.fetch_one(sql, (phone,))
            if result:
                return result.get("code")
        except Exception as e:
            print(f"查询短信验证码失败: {e}")
        return None

    def _check_user_exists(self, phone, pg_helper=None):
        """检查手机号是否存在于平台用户表

        Args:
            phone: 手机号
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            bool: 用户是否存在
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT COUNT(*) as cnt FROM cjgt_platform_user
            WHERE user_name = %s AND status = 1
        """
        try:
            result = pg_helper.fetch_one(sql, (phone,))
            if result:
                return result.get("cnt", 0) > 0
        except Exception as e:
            print(f"查询用户是否存在失败: {e}")
        return False

    def _login_with_sms_code(self, phone, pg_helper=None):
        """发送验证码并从数据库获取后登录

        Args:
            phone: 手机号
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            (token, sms_code) 元组
        """
        pg_helper = pg_helper or self._get_pg_helper()

        response = self.client.send_code(phone=phone)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        sms_code = self._get_sms_code_from_db(phone, pg_helper)
        assert sms_code, f"未从数据库获取到手机号 {phone} 的验证码"
        print(f"获取到验证码: {sms_code}")

        login_response = self.client.login_with_sms(username=phone, sms_code=sms_code)
        self.validator.assert_status_code(login_response, 200)
        login_data = login_response.json()
        self.assert_save_success(login_data)
        token = login_data.get("data", {}).get("token")
        assert token, f"登录成功但未返回 token: {login_data}"

        return token, sms_code
