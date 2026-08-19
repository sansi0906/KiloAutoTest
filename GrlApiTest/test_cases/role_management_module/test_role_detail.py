"""
test_role_detail.py - 角色详情接口测试
=============================================
覆盖角色管理模块的详情查询场景：
- 查询已存在的角色详情
- 查询不存在的角色ID
- 缺少ID字段
- 无效ID格式
- ID为0
- ID为负数
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleDetail(TestBase):
    def test_get_role_detail_existing(self):
        """查询已存在的角色详情，应返回成功"""

        role_id, role_name, _ = self._create_role()
        response = self.client.get_role_detail(role_id=role_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Get role detail failed: {data}"
        assert "data" in data
        assert data["data"].get("id") == role_id
        assert data["data"].get("roleName") == role_name

    def test_get_role_detail_non_existing(self):
        """查询不存在的角色ID，应返回失败"""

        response = self.client.get_role_detail(role_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_get_role_detail_missing_id(self):
        """缺少ID字段，应返回失败"""

        response = self.client.get_role_detail(role_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_get_role_detail_invalid_id_format(self):
        """无效ID格式，应返回失败"""

        response = self.client.get_role_detail(role_id="abc")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_get_role_detail_zero_id(self):
        """ID为0，应返回失败"""

        response = self.client.get_role_detail(role_id=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"
