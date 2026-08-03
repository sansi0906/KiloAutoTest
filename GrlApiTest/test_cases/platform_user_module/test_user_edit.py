"""
test_user_edit.py - 平台用户编辑接口测试
============================================
覆盖平台用户管理模块的编辑接口场景：
- 正常编辑用户信息
- 编辑时手机号重复
- 缺少必填字段（空真实姓名）
- 无效手机号格式
- 修改用户状态
"""

import time
import random

import pytest

from .test_base import TestBase


class TestUserEdit(TestBase):
    def _unique_real_name(self):
        """生成唯一的真实姓名，格式：测试用户+秒级时间戳"""
        return f"测试用户{int(time.time())}"

    def _unique_user_name(self):
        """生成唯一的用户名（174开头的11位纯数字手机号）"""
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    def test_edit_user_success(self):
        """使用有效参数编辑用户，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()
        new_real_name = self._unique_real_name()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name=new_real_name,
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    @pytest.mark.backend_bug
    def test_edit_user_not_exist(self):
        """编辑不存在的用户ID，预期应返回失败，但后端实际返回成功（疑似未做存在性校验）"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.edit_user(
            user_id=999999,
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 预期：编辑不存在的用户应返回失败
        # 实际后端bug：返回成功 code:00
        assert data.get("code") not in ("0", "00"), f"Expected failure for non-existent user, got: {data}"
        """编辑用户时使用已注册的手机号，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        phone1 = self._unique_user_name()
        phone2 = self._unique_user_name()
        user_id1, _, _ = self._create_user(user_name=phone1)
        user_id2, _, _ = self._create_user(user_name=phone2)

        response = self.client.edit_user(
            user_id=user_id2,
            user_name=phone1,
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_missing_real_name(self):
        """缺少 realName 字段，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name="",
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_invalid_phone(self):
        """使用无效手机号格式，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, _, _ = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name="12345",
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_change_status(self):
        """修改用户状态（启用/禁用），应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name=real_name,
            sex=1,
            role_group_id=5,
            status=0,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_edit_user_change_sex(self):
        """修改用户性别，应返回成功"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name=real_name,
            sex=0,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_edit_user_missing_id(self):
        """缺少 user_id，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.edit_user(
            user_id=None,
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_missing_user_name(self):
        """缺少 userName，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, _, _ = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name="",
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_missing_status(self):
        """缺少 status，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name=real_name,
            sex=1,
            role_group_id=5,
            status=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_missing_real_name(self):
        """缺少 realName，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, _ = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name="",
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_missing_role_group_id(self):
        """缺少 roleGroupId，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name=real_name,
            sex=1,
            role_group_id=None,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_user_missing_sex(self):
        """缺少 sex，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        user_id, user_name, real_name = self._create_user()

        response = self.client.edit_user(
            user_id=user_id,
            user_name=user_name,
            real_name=real_name,
            sex=None,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
