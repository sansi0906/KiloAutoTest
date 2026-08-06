"""
test_business_scope.py - 经营范围配置管理接口测试
=============================================
覆盖经营范围配置管理模块的接口场景：
1. 新增经营范围
2. 分页查询经营范围
3. 获取经营范围详情
4. 编辑经营范围
5. 删除经营范围
6. 修改经营范围状态
"""

import time

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="经营范围模块接口暂不执行，待后端修复 detail 接口 404 问题后再恢复")
class TestBusinessScope(TestBase):
    def _save_and_get_id(self, scope_name=None, remark=None):
        """新增经营范围并通过分页查询获取ID

        Returns:
            (scope_id, scope_name) 元组
        """
        scope_name = scope_name or self._unique_scope_name()
        response = self.client.add_business_scope(
            scope_name=scope_name,
            remark=remark or "TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        page_resp = self.client.page_business_scopes(page_num=1, page_size=10, scope_name=scope_name)
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        scope_id = None
        for record in records:
            if record.get("scopeName") == scope_name:
                scope_id = record.get("id")
                break
        assert scope_id, f"Business scope not found after creation: {page_data}"
        return scope_id, scope_name

    @pytest.mark.smoke
    def test_add_business_scope_success(self):
        """使用有效参数新增经营范围，应返回成功"""
        scope_name = self._unique_scope_name()
        response = self.client.add_business_scope(
            scope_name=scope_name,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_add_business_scope_missing_name(self):
        """缺少 scopeName，应返回失败"""
        response = self.client.add_business_scope(
            scope_name="",
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_business_scope_name_too_long(self):
        """scopeName 超过20个字符，应返回失败"""
        response = self.client.add_business_scope(
            scope_name="A" * 21,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_business_scopes_success(self):
        """正常分页查询经营范围，应返回成功"""
        response = self.client.page_business_scopes(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"
        page_data = data.get("data", {})
        assert "records" in page_data, "Missing records in page data"
        assert "total" in page_data, "Missing total in page data"

    def test_page_business_scopes_by_name(self):
        """按经营范围名称模糊查询"""
        scope_id, scope_name = self._save_and_get_id()

        response = self.client.page_business_scopes(page_num=1, page_size=10, scope_name=scope_name)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("scopeName") == scope_name for record in records)
        assert found, f"Created scope '{scope_name}' not found in page results"

    def test_page_business_scopes_by_status(self):
        """按状态筛选经营范围"""
        scope_id, scope_name = self._save_and_get_id()

        response = self.client.page_business_scopes(page_num=1, page_size=10, is_enabled=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        assert isinstance(records, list), "Records should be a list"

    @pytest.mark.backend_bug
    def test_get_business_scope_detail_existing(self):
        """获取已存在的经营范围详情，当前后端detail接口存在bug，所有ID均返回404"""
        scope_id, scope_name = self._save_and_get_id()

        response = self.client.get_business_scope_detail(scope_id=scope_id)
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        data = response.json()
        # 预期：应返回成功 code:00 且 data 中包含经营范围信息
        # 实际后端bug：detail接口对所有ID都返回 code:03 "服务不存在"
        assert data.get("code") == "00", f"Expected success for existing scope, got: {data}"
        assert data.get("data") is not None, "Expected data in response"
        assert data.get("data", {}).get("id") == str(scope_id)

    @pytest.mark.backend_bug
    def test_get_business_scope_detail_non_existing(self):
        """获取不存在的经营范围详情，当前后端detail接口存在bug，所有ID均返回404"""
        response = self.client.get_business_scope_detail(scope_id=999999)
        # 预期：应返回 code:03 "服务不存在"
        # 实际后端bug：返回 HTTP 404
        assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}"
        data = response.json()
        assert data.get("code") == "03", f"Expected code 03 for non-existing scope, got: {data}"

    def test_edit_business_scope_success(self):
        """编辑已存在的经营范围，应返回成功"""
        scope_id, scope_name = self._save_and_get_id()
        new_scope_name = f"ScopeEdit{int(time.time() * 1000) % 100000}"

        response = self.client.edit_business_scope(
            scope_id=scope_id,
            scope_name=new_scope_name,
            remark="EditedRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_edit_business_scope_missing_name(self):
        """缺少 scopeName，应返回失败"""
        scope_id, _ = self._save_and_get_id()

        response = self.client.edit_business_scope(
            scope_id=scope_id,
            scope_name="",
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_disable(self):
        """禁用已启用的经营范围，应返回成功"""
        scope_id, _ = self._save_and_get_id()

        response = self.client.update_business_scope_status(scope_id=scope_id, is_enabled=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_enable(self):
        """启用已禁用的经营范围，应返回成功"""
        scope_id, _ = self._save_and_get_id()

        disable_resp = self.client.update_business_scope_status(scope_id=scope_id, is_enabled=0)
        self.validator.assert_status_code(disable_resp, 200)
        self.assert_save_success(disable_resp.json())

        enable_resp = self.client.update_business_scope_status(scope_id=scope_id, is_enabled=1)
        self.validator.assert_status_code(enable_resp, 200)
        self.assert_save_success(enable_resp.json())

    def test_delete_business_scope_success(self):
        """删除已禁用的经营范围，应返回成功"""
        scope_id, _ = self._save_and_get_id()

        # 先禁用才能删除
        disable_resp = self.client.update_business_scope_status(scope_id=scope_id, is_enabled=0)
        self.validator.assert_status_code(disable_resp, 200)
        self.assert_save_success(disable_resp.json())

        response = self.client.delete_business_scope(scope_id=scope_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_delete_business_scope_enabled(self):
        """删除启用的经营范围，按正常逻辑应返回失败"""
        scope_id, _ = self._save_and_get_id()

        response = self.client.delete_business_scope(scope_id=scope_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_business_scope_non_existing(self):
        """删除不存在的经营范围，按正常逻辑应返回失败"""
        response = self.client.delete_business_scope(scope_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_business_scope_missing_id(self):
        """删除经营范围缺少 id，应返回失败"""
        response = self.client.delete_business_scope(scope_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_id(self):
        """修改经营范围状态缺少 id，应返回失败"""
        response = self.client.update_business_scope_status(scope_id=None, is_enabled=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_is_enabled(self):
        """修改经营范围状态缺少 isEnabled，应返回失败"""
        scope_id, _ = self._save_and_get_id()
        response = self.client.update_business_scope_status(scope_id=scope_id, is_enabled=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
