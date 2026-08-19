"""
test_role_page.py - 角色分页查询接口测试
=============================================
覆盖角色管理模块的分页查询场景：
- 正常分页查询
- 按角色名称模糊查询
- 按状态筛选
- 组合查询
- 无效页码
- 超大每页条数
- 空角色名称
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRolePage(TestBase):
    @pytest.mark.smoke
    def test_page_roles_success(self):
        """正常分页查询角色列表，应返回成功"""

        response = self.client.page_roles(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page roles failed: {data}"
        assert "data" in data
        assert "records" in data["data"]
        assert "total" in data["data"]

    def test_page_roles_by_name(self):
        """按角色名称模糊查询，应返回成功"""

        role_name = self._unique_role_name()
        self.client.save_role(role_name=role_name, status=1)

        response = self.client.page_roles(page_num=1, page_size=10, role_name=role_name[:5])
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page roles by name failed: {data}"

    def test_page_roles_by_status(self):
        """按状态筛选，应返回成功"""

        response = self.client.page_roles(page_num=1, page_size=10, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page roles by status failed: {data}"

    def test_page_roles_with_pagination(self):
        """分页参数验证，应返回成功"""

        response = self.client.page_roles(page_num=2, page_size=5)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page roles with pagination failed: {data}"
        assert data["data"]["pageNum"] == 2
        assert data["data"]["pageSize"] == 5

    def test_page_roles_invalid_page_num(self):
        """无效页码（0），应返回失败"""

        response = self.client.page_roles(page_num=0, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_page_roles_large_page_size(self):
        """超大每页条数（1000），应返回失败"""

        response = self.client.page_roles(page_num=1, page_size=1000)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_page_roles_empty_name(self):
        """空角色名称，应返回全部角色"""

        response = self.client.page_roles(page_num=1, page_size=10, role_name="")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page roles with empty name failed: {data}"
