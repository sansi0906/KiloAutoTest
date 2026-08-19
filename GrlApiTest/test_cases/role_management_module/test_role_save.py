"""
test_role_save.py - 角色保存接口测试
=============================================
覆盖角色管理模块的保存接口场景：
- 正常创建角色
- 角色名称重复
- 缺少必填字段（roleName/status）
- 空角色名称
- 空角色备注
- 无效状态值
- 超长角色名称
- 特殊字符角色名称
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：role 表/接口待确认")
class TestRoleSave(TestBase):
    @pytest.mark.smoke
    def test_save_role_success(self):
        """使用有效参数创建角色，应返回成功"""

        role_name = self._unique_role_name()
        role_remark = self._unique_role_remark()

        response = self.client.save_role(
            role_name=role_name,
            status=1,
            role_remark=role_remark,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_save_role_duplicate_name(self):
        """使用已存在的角色名称创建角色，应返回失败"""

        role_name = self._unique_role_name()
        role_remark = self._unique_role_remark()

        response_1 = self.client.save_role(
            role_name=role_name,
            status=1,
            role_remark=role_remark,
        )
        self.validator.assert_status_code(response_1, 200)
        data_1 = response_1.json()
        self.assert_save_success(data_1)

        response_2 = self.client.save_role(
            role_name=role_name,
            status=1,
            role_remark=self._unique_role_remark(),
        )
        self.validator.assert_status_code(response_2, 200)
        data_2 = response_2.json()
        self.assert_save_failure(data_2)

    def test_save_role_missing_role_name(self):
        """缺少 roleName 字段，应返回失败"""

        response = self.client.save_role(
            role_name="",
            status=1,
            role_remark=self._unique_role_remark(),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_role_missing_status(self):
        """缺少 status 字段，应返回失败"""

        response = self.client.save_role(
            role_name=self._unique_role_name(),
            status=None,
            role_remark=self._unique_role_remark(),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_role_empty_remark(self):
        """空角色备注，应返回成功"""

        response = self.client.save_role(
            role_name=self._unique_role_name(),
            status=1,
            role_remark="",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_save_role_invalid_status(self):
        """使用无效状态值，应返回失败"""

        response = self.client.save_role(
            role_name=self._unique_role_name(),
            status=99,
            role_remark=self._unique_role_remark(),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_role_name_too_long(self):
        """角色名称超过最大长度，应返回失败"""

        response = self.client.save_role(
            role_name="A" * 101,
            status=1,
            role_remark=self._unique_role_remark(),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_role_name_special_chars(self):
        """角色名称包含特殊字符，应返回成功"""

        response = self.client.save_role(
            role_name="<script>alert('xss')</script>",
            status=1,
            role_remark=self._unique_role_remark(),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
