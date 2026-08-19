"""
test_role_change_status.py - 角色状态变更接口测试
=============================================
覆盖角色管理模块的状态变更场景：
- 启用角色
- 禁用角色
- 不存在的角色ID
- 缺少ID字段
- 无效状态值
- 状态切换验证
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleChangeStatus(TestBase):
    def test_disable_existing_role(self):
        """禁用已存在的角色，应返回成功"""

        role_id, role_name, _ = self._create_role(status=1)
        response = self.client.change_role_status(role_id=role_id, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证状态已变更
        detail_resp = self.client.get_role_detail(role_id=role_id)
        self.validator.assert_status_code(detail_resp, 200)
        detail_data = detail_resp.json()
        assert detail_data["data"]["status"] == 0

    def test_enable_existing_role(self):
        """启用已存在的角色，应返回成功"""

        role_id, _, _ = self._create_role(status=0)
        response = self.client.change_role_status(role_id=role_id, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证状态已变更
        detail_resp = self.client.get_role_detail(role_id=role_id)
        self.validator.assert_status_code(detail_resp, 200)
        detail_data = detail_resp.json()
        assert detail_data["data"]["status"] == 1

    def test_change_status_non_existing_role(self):
        """变更不存在的角色状态，应返回失败"""

        response = self.client.change_role_status(role_id=999999, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_id(self):
        """缺少ID字段，应返回失败"""

        response = self.client.change_role_status(role_id=None, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_status(self):
        """缺少status字段，应返回失败"""

        role_id, _, _ = self._create_role()
        response = self.client.change_role_status(role_id=role_id, status=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
