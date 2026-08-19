"""
test_role_edit.py - 角色编辑接口测试
=============================================
覆盖角色管理模块的编辑场景：
- 正常编辑角色
- 编辑不存在的角色
- 缺少必填字段
- 空角色名称
- 空角色备注
- 无效状态值
- 超长角色名称
- 特殊字符角色名称
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleEdit(TestBase):
    def test_edit_role_success(self):
        """正常编辑角色，应返回成功"""

        role_id, role_name, role_remark = self._create_role()
        new_role_name = f"{role_name}_edited"
        new_role_remark = f"{role_remark}_edited"

        response = self.client.edit_role(
            role_id=role_id,
            role_name=new_role_name,
            status=0,
            role_remark=new_role_remark,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证编辑是否生效
        detail_resp = self.client.get_role_detail(role_id=role_id)
        self.validator.assert_status_code(detail_resp, 200)
        detail_data = detail_resp.json()
        assert detail_data["data"]["roleName"] == new_role_name
        assert detail_data["data"]["roleRemark"] == new_role_remark
        assert detail_data["data"]["status"] == 0

    def test_edit_role_not_exist(self):
        """编辑不存在的角色，应返回失败"""

        response = self.client.edit_role(
            role_id=999999,
            role_name="不存在的角色",
            status=1,
            role_remark="测试",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_role_missing_role_name(self):
        """缺少 roleName 字段，应返回失败"""

        role_id, _, _ = self._create_role()
        response = self.client.edit_role(
            role_id=role_id,
            role_name="",
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_role_missing_status(self):
        """缺少 status 字段，应返回失败"""

        role_id, role_name, _ = self._create_role()
        response = self.client.edit_role(
            role_id=role_id,
            role_name=role_name,
            status=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_role_name_too_long(self):
        """角色名称超过最大长度，应返回失败"""

        role_id, _, _ = self._create_role()
        response = self.client.edit_role(
            role_id=role_id,
            role_name="A" * 101,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_role_name_special_chars(self):
        """角色名称包含特殊字符，应返回成功"""

        role_id, _, _ = self._create_role()
        response = self.client.edit_role(
            role_id=role_id,
            role_name="<script>alert('xss')</script>",
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
