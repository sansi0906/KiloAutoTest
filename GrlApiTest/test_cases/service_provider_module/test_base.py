"""
test_base.py - 服务商管理模块测试基类
==================================================
提供服务商管理模块的通用测试设置和辅助方法
"""

import time
import random

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

    def _modified_phone(self, original_phone):
        """基于原手机号生成一个略有不同的手机号（修改最后一位），用于测试手机号变更

        Args:
            original_phone: 原手机号

        Returns:
            str: 修改后的手机号
        """
        if not original_phone or len(original_phone) != 11:
            return self._unique_phone()
        last_digit = int(original_phone[-1])
        new_last_digit = (last_digit + 1) % 10
        return original_phone[:-1] + str(new_last_digit)

    def _unique_item_name(self):
        """生成唯一的服务项目名称"""
        suffix = random.randint(1000, 9999)
        return f"Test{suffix}"

    def _create_service_item(self, item_name=None, billing_method=1):
        """新增服务项目并通过分页查询获取项目ID

        Returns:
            (item_id, item_name) 元组
        """
        item_name = item_name or self._unique_item_name()
        return self._create_and_get_id(
            create_fn=lambda: self.client.add_service_item(
                item_name=item_name,
                billing_method=billing_method,
                subtitle="TestSubtitle",
                item_desc="TestDescription",
            ),
            query_fn=lambda: self.client.page_service_items(page_num=1, page_size=10, item_name=item_name),
            match_key="itemName",
            match_value=item_name,
        )

    def _build_provider_payload(self, company_name=None, contact_phone=None, service_items=None, service_areas=None, **kwargs):
        """构建服务商新增/编辑标准入参"""
        rename = company_name or self._unique_company_name()
        mobile = contact_phone or self._unique_phone()

        payload = {
            "companyName": rename,
            "unifiedSocialCode": f"9119XX{mobile}",
            "businessLicenseUrl": "/20260813/Q5270R37403.jpg",
            "officeAddress": [
                {
                    "code": "110119000000",
                    "level": "county",
                    "name": "延庆区"
                }
            ],
            "officeAddressDetail": "延庆区测试地址",
            "serviceArea": service_areas if service_areas is not None else [
                {
                    "code": "110119000000",
                    "level": "county",
                    "name": "延庆区"
                }
            ],
            "contactPerson": rename,
            "contactPhone": mobile,
            "serviceItems": service_items if service_items is not None else [1],
            "roleGroupId": 215,
            "agencyLicenseUrl": "/20260813/ZUU06234312.png",
            "agencyPlatformScreenshotUrl": "/20260813/ZUU06234312.png",
            "taxCreditScreenshotUrl": "/20260813/ZUU06234312.png",
            "annualInspectionUrl": "/20260813/ZUU06234312.png"
        }
        payload.update(kwargs)
        return payload

    def _save_and_get_id(self, service_item_ids=None, service_areas=None, **kwargs):
        """新增服务商并通过分页查询获取ID

        Args:
            service_item_ids: 服务项目ID列表，如果为None则从分页查询获取展示的服务项目
            service_areas: 服务区域列表，如果为None则使用默认区级
            **kwargs: 其他构建参数

        Returns:
            (provider_id, company_name, contact_phone, service_items) 元组
        """
        if service_item_ids is None:
            page_resp = self.client.page_service_items(page_num=1, page_size=10, is_display=1)
            self.validator.assert_status_code(page_resp, 200)
            page_data = page_resp.json()
            records = page_data.get("data", {}).get("records", [])
            if not records:
                item_id, _ = self._create_service_item()
                service_item_ids = [item_id]
            else:
                service_item_ids = [str(record.get("id")) for record in records[:3] if record.get("id")]

        payload = self._build_provider_payload(
            service_items=service_item_ids,
            service_areas=service_areas,
            **kwargs
        )
        provider_id, _ = self._create_and_get_id(
            create_fn=lambda: self.client.post("/platform/serverUser/save", json=payload),
            query_fn=lambda: self.client.post("/platform/serverUser/page", json={
                "pageNum": 1,
                "pageSize": 10,
                "companyName": payload["companyName"]
            }),
            match_key="companyName",
            match_value=payload["companyName"],
        )
        return provider_id, payload["companyName"], payload["contactPhone"], service_item_ids

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.post("/platform/serverUser/delete", json={"id": item_id})

    def _verify_provider_in_db(self, provider_id, company_name, unified_social_code, contact_phone, office_address, service_area, service_items, pg_helper=None):
        """验证服务商数据是否存在于 PostgreSQL 数据库

        Args:
            provider_id: 服务商ID
            company_name: 公司名称
            unified_social_code: 统一社会信用代码
            contact_phone: 联系电话
            office_address: 办公地址列表
            service_area: 服务区域列表
            service_items: 服务项目ID列表
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 数据库记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, company_name, unified_social_code, business_license_url,
                   office_address, service_area, contact_person, contact_phone,
                   service_items, agency_license_url, agency_platform_screenshot_url,
                   tax_credit_screenshot_url, annual_inspection_url, status, delete_status,
                   office_address_detail, role_group_id
            FROM cjgt_service_provider
            WHERE id = %s AND company_name = %s AND contact_phone = %s AND delete_status = 0
        """
        result = pg_helper.fetch_one(sql, (provider_id, company_name, contact_phone))
        assert result, f"服务商在数据库中未找到: id={provider_id}, name={company_name}, phone={contact_phone}"

        assert result["company_name"] == company_name, f"公司名称不匹配: {result['company_name']} != {company_name}"
        assert result["unified_social_code"] == unified_social_code, f"统一社会代码不匹配: {result['unified_social_code']} != {unified_social_code}"
        assert result["contact_phone"] == contact_phone, f"联系电话不匹配: {result['contact_phone']} != {contact_phone}"
        assert result["status"] == 1, f"默认状态应为启用: {result['status']}"
        assert result.get("role_group_id") == 215, f"默认角色组ID应为215: {result.get('role_group_id')}"

        if office_address and result.get("office_address"):
            assert result["office_address"] == office_address, f"办公地址不匹配"
        if service_area and result.get("service_area"):
            assert result["service_area"] == service_area, f"服务区域不匹配"
        if service_items and result.get("service_items"):
            db_service_items = result["service_items"]
            if isinstance(db_service_items, str):
                import json
                db_service_items = json.loads(db_service_items)
            db_service_items = [int(x) for x in db_service_items]
            input_service_items = [int(x) for x in service_items]
            assert db_service_items == input_service_items, f"服务项目不匹配: {db_service_items} != {input_service_items}"

        return result

    def _verify_provider_deleted(self, provider_id, pg_helper=None):
        """验证服务商已删除（delete_status != 0）

        Args:
            provider_id: 服务商ID
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            bool: 是否已删除
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, delete_status FROM cjgt_service_provider
            WHERE id = %s
        """
        result = pg_helper.fetch_one(sql, (provider_id,))
        if result:
            return result.get("delete_status", 0) != 0
        return True

    def _verify_sms_log_for_account_creation(self, phone, pg_helper=None):
        """验证服务商创建后是否有账号开通短信，content必须包含'已开通'、'登录平台'及密码格式Cjgt@+3位数字

        Args:
            phone: 手机号
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 短信记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, phone, sms_type, content, send_time
            FROM cjgt_sms_log
            WHERE phone = %s AND sms_type = 1
            AND content LIKE %s AND content LIKE %s AND content LIKE %s
            ORDER BY send_time DESC
            LIMIT 1
        """
        result = pg_helper.fetch_one(sql, (phone, "%已开通%", "%登录平台%", "%Cjgt@%"))
        assert result, f"未找到手机号 {phone} 的账号开通短信（需包含'已开通'、'登录平台'及'Cjgt@'）"
        content = result["content"]
        import re
        password_match = re.search(r'Cjgt@\d{3}', content)
        assert password_match, f"账号开通短信中未找到Cjgt@+3位数字格式的密码: {content}"
        return result

    def _verify_sms_log_for_phone_change(self, phone, old_phone, pg_helper=None):
        """验证修改手机号后是否有账号变更短信，content必须包含'已更新'和'登录'

        Args:
            phone: 新手机号
            old_phone: 旧手机号
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 短信记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, phone, sms_type, content, send_time
            FROM cjgt_sms_log
            WHERE phone = %s AND sms_type = 1
            AND content LIKE %s AND content LIKE %s
            ORDER BY send_time DESC
            LIMIT 1
        """
        result = pg_helper.fetch_one(sql, (phone, "%已更新%", "%登录%"))
        assert result, f"未找到手机号变更短信: 旧手机号={old_phone}, 新手机号={phone}（需包含'已更新'和'登录'）"
        return result

    def _verify_sms_log_for_password_reset(self, phone, pg_helper=None):
        """验证重置密码后是否有密码重置短信，content必须包含'新密码为'或'已重置为'，且密码格式为Cjgt@+3位数字

        Args:
            phone: 手机号
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 短信记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, phone, sms_type, content, send_time
            FROM cjgt_sms_log
            WHERE phone = %s AND sms_type = 1
            AND (content LIKE %s OR content LIKE %s)
            ORDER BY send_time DESC
            LIMIT 1
        """
        result = pg_helper.fetch_one(sql, (phone, "%新密码为%", "%已重置为%"))
        assert result, f"未找到手机号 {phone} 的密码重置短信（需包含'新密码为'或'已重置为'）"
        content = result["content"]
        import re
        password_match = re.search(r'Cjgt@\d{3}', content)
        assert password_match, f"密码重置短信中未找到Cjgt@+3位数字格式的密码: {content}"
        return result
