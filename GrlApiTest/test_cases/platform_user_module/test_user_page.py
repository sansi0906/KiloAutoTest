"""
test_user_page.py - 平台用户分页查询接口测试
==============================================
覆盖平台用户管理模块的分页查询接口场景：
- 正常分页查询
- 按用户名模糊查询
- 按角色组ID筛选
- 按状态筛选
- 无效页码
- 超大页码
"""

import pytest

from .test_base import TestBase


class TestUserPage(TestBase):
    @pytest.mark.smoke
    def test_page_users_success(self):
        """正常分页查询，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"

    def test_page_users_by_user_name(self):
        """按用户名模糊查询，应返回匹配结果"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(
            page_num=1,
            page_size=10,
            user_name="测试",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_page_users_by_role_group_id(self):
        """按角色组ID筛选，应返回匹配结果"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(
            page_num=1,
            page_size=10,
            role_group_id=5,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_page_users_by_status(self):
        """按状态筛选（启用），应返回匹配结果"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(
            page_num=1,
            page_size=10,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_page_users_invalid_page_num(self):
        """使用无效页码（0），应返回失败或空结果"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(page_num=0, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 页码为0可能返回失败或空结果
        assert data.get("code") not in ("0", "00") or data.get("data", {}).get("records") == [], (
            f"Expected failure or empty result for page_num=0, got: {data}"
        )

    def test_page_users_large_page_size(self):
        """使用超大每页条数（超过100），应返回失败或限制结果"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.page_users(page_num=1, page_size=999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 超大pageSize可能返回失败或限制为100
        assert data.get("code") not in ("0", "00") or data.get("data", {}).get("size", 0) <= 100, (
            f"Expected failure or size limit for page_size=999, got: {data}"
        )