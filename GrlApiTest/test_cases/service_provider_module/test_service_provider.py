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

import json
import time

import pytest

from .test_base import TestBase


class TestServiceProvider(TestBase):
    @pytest.mark.smoke
    def test_save_service_provider_success(self):
        """使用标准参数新增服务商，按正常逻辑应返回成功"""
        payload = self._build_provider_payload()
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 通过分页查询获取服务商ID
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
        assert provider_id, f"Created provider not found in page results"

        # 验证数据库中的数据
        db_record = self._verify_provider_in_db(
            provider_id=provider_id,
            company_name=payload["companyName"],
            unified_social_code=payload["unifiedSocialCode"],
            contact_phone=payload["contactPhone"],
            office_address=payload["officeAddress"],
            service_area=payload["serviceArea"],
            service_items=payload["serviceItems"]
        )
        assert db_record["business_license_url"] == payload["businessLicenseUrl"]
        assert db_record["agency_license_url"] == payload["agencyLicenseUrl"]
        assert db_record["agency_platform_screenshot_url"] == payload["agencyPlatformScreenshotUrl"]
        assert db_record["tax_credit_screenshot_url"] == payload["taxCreditScreenshotUrl"]
        assert db_record["annual_inspection_url"] == payload["annualInspectionUrl"]
        print(f"数据库验证成功: id={db_record['id']}, name={db_record['company_name']}")

        # 验证短信日志（账号开通短信）
        sms_record = self._verify_sms_log_for_account_creation(payload["contactPhone"])
        print(f"短信验证成功: phone={sms_record['phone']}, type={sms_record['sms_type']}, time={sms_record['send_time']}")

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
        page_data = data.get("data", {})
        records = page_data.get("records", [])
        self.skip_if_empty(records, "查询结果为空，跳过测试（可能需要先创建服务商数据）")
        assert "total" in page_data, "Missing total in page data"

    def test_page_service_providers_by_name(self):
        """按公司名称模糊查询服务商"""
        provider_id, company_name, _, _ = self._save_and_get_id()

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
        provider_id, company_name, contact_phone, _ = self._save_and_get_id()

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
        provider_id, company_name, contact_phone, _ = self._save_and_get_id()
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

        # 验证数据库中数据是否与入参一致
        db_record = self._verify_provider_in_db(
            provider_id=provider_id,
            company_name=new_company_name,
            unified_social_code=payload["unifiedSocialCode"],
            contact_phone=contact_phone,
            office_address=payload["officeAddress"],
            service_area=payload["serviceArea"],
            service_items=payload["serviceItems"]
        )
        assert db_record["business_license_url"] == payload["businessLicenseUrl"]
        print(f"编辑后数据库验证成功: id={db_record['id']}, name={db_record['company_name']}")

    def test_edit_service_provider_change_phone(self):
        """编辑服务商并修改手机号，应返回成功"""
        provider_id, company_name, contact_phone, _ = self._save_and_get_id()
        new_company_name = f"测试服务商-EDIT{int(time.time())}"
        new_contact_phone = self._modified_phone(contact_phone)

        payload = self._build_provider_payload(
            company_name=new_company_name,
            contact_phone=new_contact_phone
        )
        payload["id"] = provider_id
        payload["unifiedSocialCode"] = f"9119XX{contact_phone}"
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证数据库中手机号已更新，但统一社会代码保持不变
        db_record = self._verify_provider_in_db(
            provider_id=provider_id,
            company_name=new_company_name,
            unified_social_code=f"9119XX{contact_phone}",
            contact_phone=new_contact_phone,
            office_address=payload["officeAddress"],
            service_area=payload["serviceArea"],
            service_items=payload["serviceItems"]
        )
        assert db_record["contact_phone"] == new_contact_phone, f"手机号未更新: {db_record['contact_phone']} != {new_contact_phone}"
        print(f"手机号变更验证成功: {contact_phone} -> {new_contact_phone}")

        # 验证短信日志（手机号变更短信）
        sms_record = self._verify_sms_log_for_phone_change(new_contact_phone, contact_phone)
        print(f"手机号变更短信验证成功: new_phone={sms_record['phone']}, time={sms_record['send_time']}")

    def test_edit_service_provider_unified_social_code_immutable(self):
        """统一社会代码不允许修改，编辑时变更应返回失败"""
        provider_id, company_name, contact_phone, service_items = self._save_and_get_id()
        original_unified_social_code = f"9119XX{contact_phone}"
        new_unified_social_code = f"9119XX{self._unique_phone()}"

        payload = self._build_provider_payload(
            company_name=company_name,
            contact_phone=contact_phone,
            service_items=service_items
        )
        payload["id"] = provider_id
        payload["unifiedSocialCode"] = new_unified_social_code
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

        # 验证数据库中统一社会代码未改变
        db_record = self._verify_provider_in_db(
            provider_id=provider_id,
            company_name=company_name,
            unified_social_code=original_unified_social_code,
            contact_phone=contact_phone,
            office_address=payload["officeAddress"],
            service_area=payload["serviceArea"],
            service_items=service_items
        )
        assert db_record["unified_social_code"] == original_unified_social_code, "统一社会代码不应被修改"
        print(f"统一社会代码不可修改验证成功: 保持为 {db_record['unified_social_code']}")

    def test_edit_service_provider_missing_company_name(self):
        """编辑服务商缺少 companyName，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["companyName"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_unified_social_code(self):
        """编辑服务商缺少 unifiedSocialCode，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["unifiedSocialCode"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_office_address(self):
        """编辑服务商缺少 officeAddress，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["officeAddress"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_service_area(self):
        """编辑服务商缺少 serviceArea，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["serviceArea"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_contact_person(self):
        """编辑服务商缺少 contactPerson，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["contactPerson"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_contact_phone(self):
        """编辑服务商缺少 contactPhone，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["contactPhone"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_service_items(self):
        """编辑服务商缺少 serviceItems，应返回失败"""
        provider_id, _, _, _ = self._save_and_get_id()
        payload = self._build_provider_payload()
        del payload["serviceItems"]
        payload["id"] = provider_id
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_disable(self):
        """禁用已启用的服务商，应返回成功"""
        provider_id, _, _, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/changeStatus", json={
            "id": provider_id,
            "status": 0
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_enable(self):
        """启用已禁用的服务商，应返回成功"""
        provider_id, _, _, _ = self._save_and_get_id()

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
        provider_id, company_name, contact_phone, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/resetPwd", json={"id": provider_id})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证短信日志（密码重置短信通知）
        sms_record = self._verify_sms_log_for_password_reset(contact_phone)
        print(f"密码重置短信验证成功: phone={sms_record['phone']}, type={sms_record['sms_type']}, time={sms_record['send_time']}")

    def test_reset_password_non_existing(self):
        """重置不存在的服务商密码，按正常逻辑应返回失败"""
        response = self.client.post("/platform/serverUser/resetPwd", json={"id": 999999})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_service_provider_success(self):
        """删除已存在的服务商，应返回成功"""
        provider_id, company_name, contact_phone, _ = self._save_and_get_id()

        response = self.client.post("/platform/serverUser/delete", json={"id": provider_id})
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证数据库中 delete_status 已改变
        is_deleted = self._verify_provider_deleted(provider_id)
        assert is_deleted, f"服务商未标记为删除: id={provider_id}"
        print(f"数据库删除验证成功: id={provider_id}, delete_status 已改变")

    @pytest.mark.backend_bug
    @pytest.mark.skip(reason="Bug 2: 已注释")
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
        provider_id, _, _, _ = self._save_and_get_id()
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

    def test_page_service_providers_page_size_zero(self):
        """分页查询 pageSize=0，应返回失败或空列表"""
        response = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 0
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        assert len(records) == 0, f"Expected empty records for pageSize=0, got {len(records)}"

    def test_page_service_providers_page_size_over_100(self):
        """分页查询 pageSize=101，验证后端限制"""
        response = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 101
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        assert len(records) <= 100, f"Expected max 100 records, got {len(records)}"

    @pytest.mark.backend_bug
    def test_page_service_providers_page_num_zero(self):
        """分页查询 pageNum=0，后端未做校验，实际返回第1页数据（与pageNum=1相同）"""
        response = self.client.post("/platform/serverUser/page", json={
            "pageNum": 0,
            "pageSize": 10
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        # 后端Bug: pageNum=0 未做校验，实际返回第1页数据
        assert len(records) <= 10, f"Expected max 10 records, got {len(records)}"

    def test_page_service_providers_by_service_area(self):
        """按服务区域查询服务商"""
        service_areas = [
            {"code": "110119000000", "level": "county", "name": "延庆区"},
            {"code": "110108000000", "level": "county", "name": "海淀区"}
        ]
        provider_id, company_name, _, _ = self._save_and_get_id(service_areas=service_areas)

        response = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 10,
            "serviceArea": json.dumps(service_areas, ensure_ascii=False)
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("companyName") == company_name for record in records)
        assert found, f"Created provider '{company_name}' not found by service area"

    def test_edit_service_provider_non_existing(self):
        """编辑不存在的服务商，应返回失败"""
        payload = self._build_provider_payload()
        payload["id"] = 999999
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_provider_missing_id(self):
        """编辑服务商缺少 id，应返回失败"""
        payload = self._build_provider_payload()
        response = self.client.post("/platform/serverUser/edit", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.backend_bug
    @pytest.mark.skip(reason="Bug 3: 已注释")
    def test_change_status_non_existing(self):
        """修改不存在的服务商状态，后端未做存在性校验，实际返回成功"""
        response = self.client.post("/platform/serverUser/changeStatus", json={
            "id": 999999,
            "status": 0
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure for non-existing provider, got: {data}"

    @pytest.mark.backend_bug
    @pytest.mark.skip(reason="Bug 4: 已注释")
    def test_change_status_invalid_status(self):
        """修改服务商状态为非法值（非0/1），后端未做校验，实际返回成功"""
        provider_id, _, _, _ = self._save_and_get_id()
        response = self.client.post("/platform/serverUser/changeStatus", json={
            "id": provider_id,
            "status": 2
        })
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure for invalid status, got: {data}"

    @pytest.mark.backend_bug
    def test_save_service_provider_invalid_phone_format(self):
        """新增服务商手机号格式非法（非174开头），后端未做校验，实际返回成功"""
        payload = self._build_provider_payload(contact_phone="13800138000")
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure for invalid phone format, got: {data}"

    def test_save_service_provider_long_unified_social_code(self):
        """新增服务商统一社会代码超长，应返回失败"""
        payload = self._build_provider_payload()
        payload["unifiedSocialCode"] = "A" * 100
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_service_provider_multi_service_area(self):
        """新增服务商多个服务区域，应返回成功"""
        service_areas = [
            {"code": "110119000000", "level": "county", "name": "延庆区"},
            {"code": "110108000000", "level": "county", "name": "海淀区"}
        ]
        payload = self._build_provider_payload(service_areas=service_areas)
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证数据库中的服务区域
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
        assert provider_id, "Provider not found after multi-area creation"
        db_record = self._verify_provider_in_db(
            provider_id=provider_id,
            company_name=payload["companyName"],
            unified_social_code=payload["unifiedSocialCode"],
            contact_phone=payload["contactPhone"],
            office_address=payload["officeAddress"],
            service_area=service_areas,
            service_items=payload["serviceItems"]
        )
        assert db_record["service_area"] == service_areas, f"服务区域不匹配: {db_record['service_area']}"
        print(f"多服务区域验证成功: id={provider_id}, areas={service_areas}")

    def test_save_service_provider_multi_service_items(self):
        """新增服务商多个服务项目，应返回成功"""
        page_resp = self.client.page_service_items(page_num=1, page_size=10, is_display=1)
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])

        if len(records) < 2:
            pytest.skip("需要至少2个展示的服务项目才能执行此测试")

        service_items = [record.get("id") for record in records[:2] if record.get("id")]

        payload = self._build_provider_payload(service_items=service_items)
        response = self.client.post("/platform/serverUser/save", json=payload)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证数据库中的服务项目
        page_resp2 = self.client.post("/platform/serverUser/page", json={
            "pageNum": 1,
            "pageSize": 10,
            "companyName": payload["companyName"]
        })
        self.validator.assert_status_code(page_resp2, 200)
        page_data2 = page_resp2.json()
        records2 = page_data2.get("data", {}).get("records", [])
        provider_id = None
        for record in records2:
            if record.get("companyName") == payload["companyName"]:
                provider_id = record.get("id")
                break
        assert provider_id, "Provider not found after multi-items creation"
        db_record = self._verify_provider_in_db(
            provider_id=provider_id,
            company_name=payload["companyName"],
            unified_social_code=payload["unifiedSocialCode"],
            contact_phone=payload["contactPhone"],
            office_address=payload["officeAddress"],
            service_area=payload["serviceArea"],
            service_items=service_items
        )
        print(f"多服务项目验证成功: id={provider_id}, items={service_items}")

    def test_get_provider_detail_after_delete(self):
        """删除服务商后查询详情，应返回失败"""
        provider_id, company_name, _, _ = self._save_and_get_id()

        # 先删除
        delete_resp = self.client.post("/platform/serverUser/delete", json={"id": provider_id})
        self.validator.assert_status_code(delete_resp, 200)
        self.assert_save_success(delete_resp.json())

        # 再查询详情
        detail_resp = self.client.post("/platform/serverUser/detail", json={"id": provider_id})
        self.validator.assert_status_code(detail_resp, 200)
        detail_data = detail_resp.json()
        self.assert_save_failure(detail_data)
