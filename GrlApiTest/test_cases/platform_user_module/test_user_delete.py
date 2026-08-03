"""
test_user_delete.py - 平台用户删除接口测试
============================================
覆盖平台用户管理模块的删除接口场景：
- 删除已存在的用户
- 删除不存在的用户
- 删除后分页查询确认已移除
"""

import pytest

from .test_base import TestBase


class TestUserDelete(TestBase):
    def test_delete_existing_user(self):
        """删除已存在的用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user()

        response = self.client.delete_user(user_id=user_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    @pytest.mark.backend_bug
    def test_delete_non_existing_user(self):
        """删除不存在的用户，预期应返回失败，但后端实际返回成功（疑似未做存在性校验）"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.delete_user(user_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 预期：删除不存在的用户应返回失败
        # 实际后端bug：返回成功 code:00
        assert data.get("code") not in ("0", "00"), f"Expected failure for non-existent user, got: {data}"

    def test_delete_user_not_found_after_delete(self):
        """删除用户后，分页查询应不再返回该用户"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user()

        delete_response = self.client.delete_user(user_id=user_id)
        self.validator.assert_status_code(delete_response, 200)
        delete_data = delete_response.json()
        self.assert_save_success(delete_data)

        page_response = self.client.page_users(page_num=1, page_size=10, user_name=user_name)
        self.validator.assert_status_code(page_response, 200)
        page_data = page_response.json()
        records = page_data.get("data", {}).get("records", [])
        found = any(record.get("userName") == user_name for record in records)
        assert not found, f"User {user_name} still found after deletion: {page_data}"

    def test_delete_missing_id(self):
        """缺少 id 字段，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.delete_user(user_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
