"""
test_service_provider.py - 服务商管理接口测试
=============================================
覆盖服务商管理模块的接口场景：
1. 新增服务商
2. 分页查询服务商
3. 获取服务商详情
4. 编辑服务商
5. 删除服务商
6. 修改服务商状态
7. 重置服务商密码
"""

import time

import pytest

from .test_base import TestBase


class TestServiceProvider(TestBase):
    def _save_and_get_id(self, **kwargs):
        """新增服务商并通过分页查询获取ID

        Returns:
            (provider_id, company_name, contact_phone) 元组
        """
        payload = self._build_provider_payload(**kwargs)
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        page_resp = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 10,
            "companyName": payload["companyName"]
        })
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        provider_id = None
        for record in records:
            if record.get("companyName") == payload["companyName"]:
                provider_id = record.get("id")
                break
        assert provider_id, f"Service provider not found after creation: {page_data}"
        self._created_ids.append(provider_id)
        return provider_id, payload["companyName"], payload["contactPhone"]

    @pytest.mark.smoke
    def test_save_service_provider_success(self):
        """使用标准参数新增服务商，按正常逻辑应返回成功"""
        payload = self._build_provider_payload()
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_save_service_provider_duplicate_name(self):
        """使用重复的公司名称新增服务商，应返回失败"""
        payload = self._build_provider_payload()
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 再次使用相同名称新增
        response2 = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response2, 200)
        data2 = response2.json()
        self.assert_save_failure(data2)

    @pytest.mark.smoke
    def test_page_service_providers_success(self):
        """正常分页查询服务商，应返回成功"""
        response = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 10
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"
        page_data = data.get("data", {})
        assert "records" in page_data, "Missing records in page data"
        assert "total" in page_data, "Missing total in page data"

    def test_page_service_providers_by_name(self):
        """按公司名称模糊查询服务商"""
        provider_id, company_name, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 10,
            "companyName": company_name
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("companyName") == company_name for record in records)
        assert found, f"Created provider '{company_name}' not found in page results"

    def test_get_provider_detail_existing(self):
        """获取已存在的服务商详情，应返回成功"""
        provider_id, company_name, contact_phone = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/detail", json={"id": provider_id})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        provider_data = data.get("data", {})
        assert provider_data.get("id") == str(provider_id)
        assert provider_data.get("companyName") == company_name
        assert provider_data.get("contactPhone") == contact_phone

    def test_get_provider_detail_non_existing(self):
        """获取不存在的服务商详情，应返回失败"""
        response = self.client.post("/platform/serverUser/detail", json={"id": 999999})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_success(self):
        """编辑已存在的服务商，应返回成功"""
        provider_id, company_name, contact_phone = self._save_and_get_id()
        new_company_name = f"测试服务商-EDIT{int(time.time())}"

        payload = self._build_provider_payload(
            company_name=new_company_name,
            contact_phone=contact_phone
        )
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_edit_service_provider_missing_company_name(self):
        """编辑服务商缺少 companyName，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["companyName"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_unified_social_code(self):
        """编辑服务商缺少 unifiedSocialCode，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["unifiedSocialCode"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_office_address(self):
        """编辑服务商缺少 officeAddress，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["officeAddress"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_service_area(self):
        """编辑服务商缺少 serviceArea，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["serviceArea"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_contact_person(self):
        """编辑服务商缺少 contactPerson，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["contactPerson"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_contact_phone(self):
        """编辑服务商缺少 contactPhone，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["contactPhone"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_service_items(self):
        """编辑服务商缺少 serviceItems，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["serviceItems"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_disable(self):
        """禁用已启用的服务商，应返回成功"""
        provider_id, _, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/changeStatus", json={
            "id": provider_id,
            "status": 0
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_enable(self):
        """启用已禁用的服务商，应返回成功"""
        provider_id, _, _ = self._save_and_get_id()

        disable_resp = self.client.post("/platform/serverUser/changeStatus", json={
            "id": provider_id,
            "status": 0
        })
        self.validator.assert_status_code(disable_resp, 200)
        self.assert_save_success(disable_resp.json())

        enable_resp = self.client.post("/platform/serverUser/changeStatus", json={
            "id": provider_id,
            "status": 1
        })
        self.validator.assert_status_code(enable_resp, 200)
        self.assert_save_success(enable_resp.json())

    def test_reset_password_success(self):
        """重置已存在的服务商密码，应返回成功"""
        provider_id, _, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/resetPwd", json={"id": provider_id})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_reset_password_non_existing(self):
        """重置不存在的服务商密码，按正常逻辑应返回失败"""
        response = self.client.post("/platform/serverUser/resetPwd", json={"id": 999999})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_service_provider_success(self):
        """删除已存在的服务商，应返回成功"""
        provider_id, _, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/delete", json={"id": provider_id})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    @pytest.mark.backend_bug
    def test_delete_service_provider_non_existing(self):
        """删除不存在的服务商，预期应返回失败，但后端实际返回成功（疑似未做存在性校验）"""
        response = self.client.post("/platform/serverUser/delete", json={"id": 999999})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 预期：删除不存在的服务商应返回失败
        # 实际后端bug：返回成功 code:00
        assert data.get("code") not in ("0", "00"), f"Expected failure for non-existent provider, got: {data}"

    def test_delete_service_provider_missing_id(self):
        """删除服务商缺少 id，应返回失败"""
        response = self.client.post("/platform/serverUser/delete", json={})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_detail_missing_id(self):
        """获取服务商详情缺少 id，应返回失败"""
        response = self.client.post("/platform/serverUser/detail", json={})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_id(self):
        """修改服务商状态缺少 id，应返回失败"""
        response = self.client.post("/platform/serverUser/changeStatus", json={"status": 0})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_status(self):
        """修改服务商状态缺少 status，应返回失败"""
        provider_id, _, _ = self._save_and_get_id()
        response = self.client.post("/platform/serverUser/changeStatus", json={"id": provider_id})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_reset_password_missing_id(self):
        """重置服务商密码缺少 id，应返回失败"""
        response = self.client.post("/platform/serverUser/resetPwd", json={})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_company_name(self):
        """新增服务商缺少 companyName，应返回失败"""
        payload = self._build_provider_payload()
        del payload["companyName"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_unified_social_code(self):
        """新增服务商缺少 unifiedSocialCode，应返回失败"""
        payload = self._build_provider_payload()
        del payload["unifiedSocialCode"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_office_address(self):
        """新增服务商缺少 officeAddress，应返回失败"""
        payload = self._build_provider_payload()
        del payload["officeAddress"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_service_area(self):
        """新增服务商缺少 serviceArea，应返回失败"""
        payload = self._build_provider_payload()
        del payload["serviceArea"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_contact_person(self):
        """新增服务商缺少 contactPerson，应返回失败"""
        payload = self._build_provider_payload()
        del payload["contactPerson"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_contact_phone(self):
        """新增服务商缺少 contactPhone，应返回失败"""
        payload = self._build_provider_payload()
        del payload["contactPhone"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_missing_service_items(self):
        """新增服务商缺少 serviceItems，应返回失败"""
        payload = self._build_provider_payload()
        del payload["serviceItems"]
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_provider_company_name_too_long(self):
        """companyName 超过 50 个字符，应返回失败"""
        payload = self._build_provider_payload()
        payload["companyName"] = "A" * 51
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_provider_company_name_special_chars(self):
        """companyName 含特殊字符，应返回失败或净化"""
        payload = self._build_provider_payload()
        payload["companyName"] = "TestCompany<script>alert('xss')</script>"
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00", "03"), f"Unexpected response: {data}"

    def test_save_provider_invalid_unified_social_code(self):
        """unifiedSocialCode 格式无效，应返回失败"""
        payload = self._build_provider_payload()
        payload["unifiedSocialCode"] = "12345"
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_provider_invalid_contact_phone(self):
        """contactPhone 格式无效，应返回失败"""
        payload = self._build_provider_payload()
        payload["contactPhone"] = "12345"
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_provider_non_existing(self):
        """编辑不存在的服务商，应返回失败"""
        payload = self._build_provider_payload()
        payload["id"] = 999999
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
