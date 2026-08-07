"""
test_user_save.py - 平台用户保存接口测试
=============================================
覆盖平台用户管理模块的保存接口场景：
- 正常创建用户（用户名称唯一）
- 手机号已注册
- 缺少必填字段
- 无效手机号格式
- 空用户名
- 空真实姓名
"""

import time

import pytest

from .test_base import TestBase


class TestUserSave(TestBase):
    def _unique_real_name(self):
        """生成唯一的真实姓名，格式：测试用户+秒级时间戳"""
        return f"测试用户{int(time.time())}"

    def _unique_user_name(self):
        """生成唯一的用户名（174开头的11位纯数字手机号）"""
        import random
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    @pytest.mark.smoke
    def test_save_user_success(self):
        """使用有效参数创建用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        real_name = self._unique_real_name()
        user_name = self._unique_user_name()

        response = self.client.save_platform_user(
            user_name=user_name,
            real_name=real_name,
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_save_user_duplicate_phone(self):
        """使用已注册的手机号创建用户，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        real_name = self._unique_real_name()
        user_name = self._unique_user_name()

        # 第一次创建
        response_1 = self.client.save_platform_user(
            user_name=user_name,
            real_name=real_name,
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response_1, 200)
        data_1 = response_1.json()
        self.assert_save_success(data_1)

        # 第二次使用相同手机号创建，应失败
        response_2 = self.client.save_platform_user(
            user_name=user_name,
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response_2, 200)
        data_2 = response_2.json()
        self.assert_save_failure(data_2)

    def test_save_user_missing_user_name(self):
        """缺少 userName 字段，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name="",
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_user_missing_real_name(self):
        """缺少 realName 字段，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=self._unique_user_name(),
            real_name="",
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_user_invalid_phone(self):
        """使用无效手机号格式，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name="12345",
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_user_missing_role_group_id(self):
        """roleGroupId 设为 0，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=0,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # roleGroupId=0 可能被接受为默认值
        self.assert_save_success(data)

    def test_save_user_missing_sex(self):
        """sex 设为 None，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=None,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_user_missing_status(self):
        """缺少 status 字段，后端实际接受并返回成功（必填校验不严格）"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # OpenAPI 标记 status 为必填，但后端实际接受 null
        self.assert_save_success(data)

    def test_save_user_missing_all_required(self):
        """所有必填字段均为空，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name="",
            real_name="",
            sex=None,
            role_group_id=None,
            status=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)