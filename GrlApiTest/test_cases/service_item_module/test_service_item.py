"""
test_service_item.py - 服务项目配置管理接口测试
=============================================
覆盖服务项目配置管理模块的接口场景，按以下顺序验证：
1. 新增服务项目
2. 分页查询服务项目
3. 切换服务项目展示状态
4. 获取展示状态的服务项目列表
5. 编辑服务项目
"""

import time
import random

import pytest

from .test_base import TestBase


class TestServiceItem(TestBase):
    def _unique_item_name(self):
        """生成唯一的服务项目名称（最长10个字符）"""
        suffix = random.randint(1000, 9999)
        return f"Test{suffix}"

    def _create_service_item(self, item_name=None, billing_method=1):
        """新增服务项目并通过分页查询获取项目ID"""
        item_name = item_name or self._unique_item_name()
        response = self.client.add_service_item(
            item_name=item_name,
            billing_method=billing_method,
            subtitle="TestSubtitle",
            item_desc="TestDescription",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        page_resp = self.client.page_service_items(page_num=1, page_size=10, item_name=item_name)
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        item_id = None
        for record in records:
            if record.get("itemName") == item_name:
                item_id = record.get("id")
                break
        assert item_id, f"Service item not found after creation: {page_data}"
        return item_id, item_name

    @pytest.mark.smoke
    def test_add_service_item_success(self):
        """使用有效参数新增服务项目，应返回成功"""
        item_name = self._unique_item_name()
        response = self.client.add_service_item(
            item_name=item_name,
            billing_method=1,
            subtitle="TestSubtitle",
            item_desc="TestDescription",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_add_service_item_missing_name(self):
        """缺少 itemName，应返回失败"""
        response = self.client.add_service_item(
            item_name="",
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_service_item_name_too_long(self):
        """itemName 超过10个字符，应返回失败"""
        response = self.client.add_service_item(
            item_name="ThisNameIsTooLong",
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_service_items_success(self):
        """正常分页查询服务项目，应返回成功"""
        response = self.client.page_service_items(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"
        page_data = data.get("data", {})
        assert "records" in page_data, "Missing records in page data"
        assert "total" in page_data, "Missing total in page data"

    def test_page_service_items_by_name(self):
        """按服务项目名称模糊查询，应返回匹配结果"""
        item_id, item_name = self._create_service_item()

        response = self.client.page_service_items(page_num=1, page_size=10, item_name=item_name)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("itemName") == item_name for record in records)
        assert found, f"Created item '{item_name}' not found in page results"

    def test_list_display_service_items(self):
        """获取展示状态的服务项目列表，应返回成功"""
        response = self.client.list_display_service_items()
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"
        display_list = data.get("data", [])
        assert isinstance(display_list, list), "Display list should be an array"

    def test_list_display_service_items_filter(self):
        """按展示状态筛选服务项目列表"""
        item_id, item_name = self._create_service_item()

        response = self.client.list_display_service_items(is_display=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        display_list = data.get("data", [])
        assert isinstance(display_list, list), "Display list should be an array"

    def test_update_status_disable(self):
        """禁用已启用的服务项目，应返回成功"""
        item_id, item_name = self._create_service_item()

        response = self.client.update_service_item_status(item_id=item_id, is_display=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_update_status_enable(self):
        """启用已禁用的服务项目，应返回成功"""
        item_id, item_name = self._create_service_item()

        disable_resp = self.client.update_service_item_status(item_id=item_id, is_display=0)
        self.validator.assert_status_code(disable_resp, 200)
        disable_data = disable_resp.json()
        self.assert_save_success(disable_data)

        enable_resp = self.client.update_service_item_status(item_id=item_id, is_display=1)
        self.validator.assert_status_code(enable_resp, 200)
        enable_data = enable_resp.json()
        self.assert_save_success(enable_data)

    def test_edit_service_item_success(self):
        """使用有效参数编辑服务项目，应返回成功"""
        item_id, item_name = self._create_service_item()

        response = self.client.edit_service_item(
            item_id=item_id,
            item_name="Edit" + item_name[-4:],
            billing_method=2,
            subtitle="EditedSubtitle",
            item_desc="EditedDescription",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_edit_service_item_missing_name(self):
        """缺少 itemName，应返回失败"""
        item_id, _ = self._create_service_item()

        response = self.client.edit_service_item(
            item_id=item_id,
            item_name="",
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_item_missing_id(self):
        """编辑服务项目缺少 id，应返回失败"""
        response = self.client.edit_service_item(
            item_id=None,
            item_name="TestItem",
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_service_item_missing_billing_method(self):
        """编辑服务项目缺少 billingMethod，应返回失败"""
        item_id, item_name = self._create_service_item()

        response = self.client.edit_service_item(
            item_id=item_id,
            item_name=item_name,
            billing_method=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_service_item_missing_billing_method(self):
        """新增服务项目缺少 billingMethod，应返回失败"""
        response = self.client.add_service_item(
            item_name="TestItem",
            billing_method=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_service_item_missing_item_name(self):
        """新增服务项目缺少 itemName，应返回失败"""
        response = self.client.add_service_item(
            item_name="",
            billing_method=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_status_missing_id(self):
        """切换服务项目展示状态缺少 id，应返回失败"""
        response = self.client.update_service_item_status(item_id=None, is_display=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_status_missing_is_display(self):
        """切换服务项目展示状态缺少 isDisplay，应返回失败"""
        item_id, _ = self._create_service_item()
        response = self.client.update_service_item_status(item_id=item_id, is_display=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
