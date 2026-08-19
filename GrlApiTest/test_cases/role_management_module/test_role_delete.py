"""
test_role_delete.py - 角色删除接口测试
=============================================
覆盖角色管理模块的删除场景：
- 正常删除角色
- 删除不存在的角色
- 缺少ID字段
- ID为0
- ID为负数
- 删除后验证不存在
- 重复删除同一角色
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleDelete(TestBase):
    def test_delete_role_success(self):
        """正常删除角色，应返回成功"""

        role_id, role_name, _ = self._create_role()
        response = self.client.delete_role(role_id=role_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证删除后查询详情失败
        detail_resp = self.client.get_role_detail(role_id=role_id)
        self.validator.assert_status_code(detail_resp, 200)
        detail_data = detail_resp.json()
        assert detail_data.get("code") not in ("0", "00"), f"Expected not found but got: {detail_data}"

    def test_delete_role_non_existing(self):
        """删除不存在的角色，应返回失败"""

        response = self.client.delete_role(role_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_role_missing_id(self):
        """缺少ID字段，应返回失败"""

        response = self.client.delete_role(role_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_role_zero_id(self):
        """ID为0，应返回失败"""

        response = self.client.delete_role(role_id=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_role_negative_id(self):
        """ID为负数，应返回失败"""

        response = self.client.delete_role(role_id=-1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_role_not_found_after_delete(self):
        """删除后再次查询，应返回不存在"""

        role_id, _, _ = self._create_role()
        self.client.delete_role(role_id=role_id)

        detail_resp = self.client.get_role_detail(role_id=role_id)
        self.validator.assert_status_code(detail_resp, 200)
        detail_data = detail_resp.json()
        assert detail_data.get("code") not in ("0", "00"), f"Expected not found but got: {detail_data}"
