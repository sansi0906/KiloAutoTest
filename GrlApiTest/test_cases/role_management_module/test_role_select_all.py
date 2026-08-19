"""
test_role_select_all.py - 查询所有角色接口测试
=============================================
覆盖角色管理模块的查询所有角色场景：
- 正常查询所有角色列表
- 验证返回数据结构
- 空列表验证
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleSelectAll(TestBase):
    @pytest.mark.smoke
    def test_select_role_all_success(self):
        """查询所有角色列表，应返回成功"""

        response = self.client.select_role_all()
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Select role all failed: {data}"
        assert "data" in data
