"""
test_role_menu.py - 角色菜单权限接口测试
=============================================
覆盖角色管理模块的菜单权限场景：
- 为角色分配菜单权限
- 查询角色菜单权限
- 分配不存在的角色菜单
- 缺少角色ID
- 空菜单ID列表
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleMenu(TestBase):
    def test_select_menus_by_role_id_success(self):
        """查询角色菜单权限，应返回成功"""

        role_id, _, _ = self._create_role()
        response = self.client.select_menus_by_role_id(role_id=role_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Select menus by role id failed: {data}"
        assert "data" in data

    def test_select_menus_by_role_id_non_existing(self):
        """查询不存在的角色菜单权限，应返回失败"""

        response = self.client.select_menus_by_role_id(role_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_add_role_menu_success(self):
        """为角色分配菜单权限，应返回成功"""

        role_id, _, _ = self._create_role()
        response = self.client.add_role_menu(role_id=role_id, menu_ids=[1, 2, 3])
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_add_role_menu_non_existing_role(self):
        """为不存在的角色分配菜单权限，应返回失败"""

        response = self.client.add_role_menu(role_id=999999, menu_ids=[1, 2, 3])
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_role_menu_missing_role_id(self):
        """缺少角色ID，应返回失败"""

        response = self.client.add_role_menu(role_id=None, menu_ids=[1, 2, 3])
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_role_menu_empty_menu_ids(self):
        """空菜单ID列表，应返回失败"""

        role_id, _, _ = self._create_role()
        response = self.client.add_role_menu(role_id=role_id, menu_ids=[])
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
