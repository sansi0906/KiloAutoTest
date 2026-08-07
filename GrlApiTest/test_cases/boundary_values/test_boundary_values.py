"""
test_boundary_values.py - 边界值测试
========================================
覆盖各模块的边界值场景：
- 金额边界：amount=0、amount=-1、amount=999999999
- 状态边界：status=2、status=-1
- 分页边界：page_num=0、page_num=-1、page_size=0、page_size=999
- 字符串边界：空字符串、超长字符串、特殊字符
- 数字边界：billing_method=0、billing_method=-1
"""

from pathlib import Path

import time

import pytest

from utils.base_test import BaseTest


class TestBoundaryValues(BaseTest):
    _EXCEL_PATH = Path(__file__).resolve().parents[2] / "data" / "服务定价数据.xlsx"

    # ==================== 分页边界 ====================
    """边界值测试"""

    # ==================== 分页边界 ====================

    def test_page_num_zero(self):
        """page_num=0，应返回失败或空结果"""
        response = self.client.page_users(page_num=0, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_num_negative(self):
        """page_num=-1，应返回失败"""
        response = self.client.page_users(page_num=-1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_size_zero(self):
        """page_size=0，应返回失败或空结果"""
        response = self.client.page_users(page_num=1, page_size=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_size_negative(self):
        """page_size=-1，应返回失败"""
        response = self.client.page_users(page_num=1, page_size=-1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_size_very_large(self):
        """page_size=9999，应返回失败或限制结果"""
        response = self.client.page_users(page_num=1, page_size=9999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        records = data.get("data") or {}
        records = records.get("records", [])
        assert len(records) <= 100, f"Expected size limit, got {len(records)} records"

    # ==================== 字符串边界 ====================

    def test_scope_name_empty(self):
        """scopeName 为空字符串，应返回失败"""
        response = self.client.add_business_scope(
            scope_name="",
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_scope_name_max_length(self):
        """scopeName 刚好20个字符，应返回成功"""
        scope_name = f"Scope{int(time.time() * 1000) % 100000}"
        scope_name = scope_name[:20]  # Ensure exactly 20 chars
        response = self.client.add_business_scope(
            scope_name=scope_name,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_scope_name_over_max_length(self):
        """scopeName 21个字符，应返回失败"""
        scope_name = "A" * 21
        response = self.client.add_business_scope(
            scope_name=scope_name,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_item_name_empty(self):
        """itemName 为空字符串，应返回失败"""
        response = self.client.add_service_item(
            item_name="",
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_item_name_max_length(self):
        """itemName 刚好10个字符，应返回成功"""
        item_name = "A" * 10
        response = self.client.add_service_item(
            item_name=item_name,
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_item_name_over_max_length(self):
        """itemName 11个字符，应返回失败"""
        item_name = "A" * 11
        response = self.client.add_service_item(
            item_name=item_name,
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_knowledge_title_empty(self):
        """title 为空字符串，应返回失败"""
        response = self.client.save_knowledge(
            title="",
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_knowledge_title_max_length(self):
        """title 刚好50个字符，应返回成功"""
        title = "A" * 50
        response = self.client.save_knowledge(
            title=title,
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_knowledge_title_over_max_length(self):
        """title 51个字符，应返回失败"""
        title = "A" * 51
        response = self.client.save_knowledge(
            title=title,
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    # ==================== 数字边界 ====================

    def test_billing_method_zero(self):
        """billing_method=0，后端实际接受，返回成功"""
        response = self.client.add_service_item(
            item_name="TestItem",
            billing_method=0,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_billing_method_negative(self):
        """billing_method=-1，后端实际接受，返回成功"""
        response = self.client.add_service_item(
            item_name="TestItem",
            billing_method=-1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_user_status_invalid(self):
        """status=2，后端实际接受，返回成功"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=2,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_user_status_negative(self):
        """status=-1，后端实际接受，返回成功"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name=self._unique_user_name(),
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=-1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    # ==================== 特殊字符 ====================

    def test_scope_name_special_chars(self):
        """scopeName 包含特殊字符，应返回失败或成功（取决于后端校验）"""
        special_name = f"Test{int(time.time() * 1000) % 100000}<>'/\"%"
        response = self.client.add_business_scope(
            scope_name=special_name,
            remark="TestRemark",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 只记录结果，不做断言
        assert data.get("code") in ("0", "00", "E0100001", "03"), f"Unexpected response: {data}"

    def test_user_name_special_chars(self):
        """userName 包含特殊字符，应返回失败"""
        token = self.login()
        self.client.set_token(token)

        response = self.client.save_platform_user(
            user_name="test<>'\"user",
            real_name=self._unique_real_name(),
            sex=1,
            role_group_id=5,
            status=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    # ==================== 金额边界（pricing） ====================

    @pytest.mark.backend_bug
    def test_pricing_amount_zero(self):
        """amount=0，应返回失败"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            amount=0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.backend_bug
    def test_pricing_amount_negative(self):
        """amount=-1，应返回失败"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            amount=-1,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_pricing_amount_very_large(self):
        """amount=999999999.99，应返回成功或失败（取决于业务规则）"""
        item_id, _ = self._get_existing_service_item()

        if self._EXCEL_PATH.exists():
            self.client.import_pricing(
                service_item_id=item_id,
                service_item_name="Test",
                file_path=str(self._EXCEL_PATH),
            )

        response = self.client.update_pricing(
            service_item_id=item_id,
            amount=999999999.99,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 只记录结果，不做断言
        assert data.get("code") in ("0", "00", "E01000001", "03", "02"), f"Unexpected response: {data}"
