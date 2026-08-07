"""
test_base.py - 服务商管理模块测试基类
===================================================
提供服务商管理模块的通用测试设置和辅助方法
"""

import random
import time

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "service_provider_module"
    _module_desc = "服务商管理模块"

    def _unique_company_name(self):
        """生成唯一的服务商名称"""
        rename = str(int(time.time()))[-4:]
        return f"测试服务商-{rename}"

    def _unique_phone(self):
        """生成唯一的手机号（174开头）"""
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    def _build_provider_payload(self, company_name=None, contact_phone=None, service_items=None, **kwargs):
        """构建服务商新增/编辑标准入参"""
        rename = company_name or self._unique_company_name()
        mobile = contact_phone or self._unique_phone()

        payload = {
            "companyName": rename,
            "unifiedSocialCode": f"9119XX{mobile}",
            "businessLicenseUrl": "",
            "officeAddress": [
                {
                    "code": "110119000000",
                    "level": "county",
                    "name": "延庆区"
                }
            ],
            "serviceArea": [
                {
                    "code": "110000000000",
                    "level": "province",
                    "name": "北京市"
                }
            ],
            "contactPerson": rename,
            "contactPhone": mobile,
            "serviceItems": service_items if service_items is not None else [1],
            "agencyLicenseUrl": "",
            "agencyPlatformScreenshotUrl": "",
            "taxCreditScreenshotUrl": "",
            "annualInspectionUrl": ""
        }
        payload.update(kwargs)
        return payload

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
        self._log_test_data_created(provider_id, payload["companyName"])
        return provider_id, payload["companyName"], payload["contactPhone"]

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.post("/platform/serverUser/delete", json={"id": item_id})
