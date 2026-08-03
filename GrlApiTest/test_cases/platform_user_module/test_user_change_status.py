"""
test_user_change_status.py - 平台用户修改状态接口测试
=============================================
覆盖平台用户管理模块的修改状态接口场景：
- 禁用已启用的用户
- 启用已禁用的用户
- 修改不存在的用户状态
"""

import pytest

from .test_base import TestBase


class TestUserChangeStatus(TestBase):
    def test_disable_existing_user(self):
        """禁用已启用的用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user(status=1)

        response = self.client.change_user_status(user_id=user_id, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_enable_existing_user(self):
        """启用已禁用的用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user(status=0)

        response = self.client.change_user_status(user_id=user_id, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    @pytest.mark.backend_bug
    def test_change_status_non_existing_user(self):
        """修改不存在的用户状态，预期应返回失败，但后端实际返回成功（疑似未做存在性校验）"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.change_user_status(user_id=999999, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 预期：修改不存在用户状态应返回失败
        # 实际后端bug：返回成功 code:00
        assert data.get("code") not in ("0", "00"), f"Expected failure for non-existent user, got: {data}"

    def test_change_status_missing_id(self):
        """缺少 id 字段，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.change_user_status(user_id=None, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_status(self):
        """缺少 status 字段，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, _, _ = self._create_user()

        response = self.client.change_user_status(user_id=user_id, status=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
