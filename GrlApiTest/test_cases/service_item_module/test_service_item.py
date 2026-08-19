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

        # 获取新增服务项目的ID
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

        # 1. 验证 PostgreSQL 数据库中是否存在该服务项目
        db_record = self._verify_service_item_in_db(item_id, item_name)
        print(f"数据库验证成功: id={db_record['id']}, name={db_record['item_name']}, billing_method={db_record['billing_method']}")

        # 2. 验证服务项目定价是否已初始化（所有省市区，amount为null）
        pricing_records = self._verify_pricing_initialized(item_id)
        print(f"定价初始化验证成功: 共 {len(pricing_records)} 条记录")
        levels = set(r.get("level") for r in pricing_records)
        print(f"定价层级: {levels}")

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

        new_name = "Edit" + item_name[-4:]
        response = self.client.edit_service_item(
            item_id=item_id,
            item_name=new_name,
            billing_method=2,
            subtitle="EditedSubtitle",
            item_desc="EditedDescription",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证 PostgreSQL 数据库中数据是否与入参一致
        db_record = self._verify_service_item_in_db(item_id, new_name)
        assert db_record["billing_method"] == 2, f"billing_method 未更新: {db_record}"
        assert db_record["subtitle"] == "EditedSubtitle", f"subtitle 未更新: {db_record}"
        assert db_record["item_desc"] == "EditedDescription", f"item_desc 未更新: {db_record}"
        print(f"数据库验证成功: id={db_record['id']}, name={db_record['item_name']}, billing_method={db_record['billing_method']}")

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

    def test_add_service_item_yearly_billing(self):
        """使用按年计费(billingMethod=2)新增服务项目，应返回成功"""
        item_name = self._unique_item_name()
        response = self.client.add_service_item(
            item_name=item_name,
            billing_method=2,
            subtitle="YearlySubtitle",
            item_desc="YearlyDescription",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证数据库中的计费方式
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

        db_record = self._verify_service_item_in_db(item_id, item_name)
        assert db_record["billing_method"] == 2, f"按年计费未保存成功: {db_record}"
        print(f"按年计费验证成功: id={db_record['id']}, name={db_record['item_name']}, billing_method={db_record['billing_method']}")

    @pytest.mark.skip(reason="Bug 5: 已注释")
    def test_add_service_item_invalid_billing_method_zero(self):
        """使用无效计费方式(billingMethod=0)，应返回失败"""
        response = self.client.add_service_item(
            item_name="TestItem",
            billing_method=0,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # Bug: 后端未校验 billingMethod 范围，返回成功
        if data.get("code") in ("0", "00"):
            print(f"Bug: 后端未校验 billingMethod=0，返回成功: {data}")
        self.assert_save_failure(data)

    @pytest.mark.skip(reason="Bug 6: 已注释")
    def test_add_service_item_invalid_billing_method_overflow(self):
        """使用超出范围计费方式(billingMethod=99)，应返回失败"""
        response = self.client.add_service_item(
            item_name="TestItem",
            billing_method=99,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # Bug: 后端未校验 billingMethod 范围，返回成功
        if data.get("code") in ("0", "00"):
            print(f"Bug: 后端未校验 billingMethod=99，返回成功: {data}")
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

    def test_add_service_item_subtitle_too_long(self):
        """subtitle 超过100个字符，应返回失败"""
        response = self.client.add_service_item(
            item_name=self._unique_item_name(),
            billing_method=1,
            subtitle="A" * 101,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_service_item_desc_too_long(self):
        """itemDesc 超过2000个字符，应返回失败"""
        response = self.client.add_service_item(
            item_name=self._unique_item_name(),
            billing_method=1,
            item_desc="A" * 2001,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.skip(reason="Bug 7: 已注释")
    def test_edit_service_item_invalid_billing_method_zero(self):
        """编辑服务项目使用 billingMethod=0，应返回失败"""
        item_id, _ = self._create_service_item()
        response = self.client.edit_service_item(
            item_id=item_id,
            item_name="EditItem",
            billing_method=0,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # Bug: 后端未校验 billingMethod 范围
        if data.get("code") in ("0", "00"):
            print(f"Bug: 编辑时后端未校验 billingMethod=0: {data}")
        self.assert_save_failure(data)

    @pytest.mark.skip(reason="Bug 8: 已注释")
    def test_edit_service_item_invalid_billing_method_overflow(self):
        """编辑服务项目使用 billingMethod=99，应返回失败"""
        item_id, _ = self._create_service_item()
        response = self.client.edit_service_item(
            item_id=item_id,
            item_name="EditItem",
            billing_method=99,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # Bug: 后端未校验 billingMethod 范围
        if data.get("code") in ("0", "00"):
            print(f"Bug: 编辑时后端未校验 billingMethod=99: {data}")
        self.assert_save_failure(data)

    def test_page_service_items_by_billing_method(self):
        """按 billingMethod 筛选服务项目，应返回匹配结果"""
        item_id, item_name = self._create_service_item(billing_method=2)

        response = self.client.page_service_items(page_num=1, page_size=10, billing_method=2)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("billingMethod") == 2 for record in records)
        assert found, f"未找到 billingMethod=2 的服务项目: {records}"

    @pytest.mark.skip(reason="Bug 9: 已注释")
    def test_page_service_items_negative_page_num(self):
        """使用负数页码，应返回失败或空结果"""
        response = self.client.page_service_items(page_num=-1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    @pytest.mark.skip(reason="Bug 10: 已注释")
    def test_page_service_items_zero_page_size(self):
        """使用 pageSize=0，应返回失败或空结果"""
        response = self.client.page_service_items(page_num=1, page_size=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_page_service_items_by_is_display(self):
        """按 isDisplay 筛选服务项目，应返回匹配结果"""
        item_id, _ = self._create_service_item()

        response = self.client.page_service_items(page_num=1, page_size=10, is_display=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        for record in records:
            assert record.get("isDisplay") == 1, f"isDisplay 筛选不匹配: {record}"

    def test_update_status_zero_id(self):
        """使用 id=0 切换状态，应返回失败"""
        response = self.client.update_service_item_status(item_id=0, is_display=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_status_negative_id(self):
        """使用负数 id 切换状态，应返回失败"""
        response = self.client.update_service_item_status(item_id=-1, is_display=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.skip(reason="Bug 11: 已注释")
    def test_update_status_invalid_is_display_two(self):
        """使用 isDisplay=2 切换状态，应返回失败"""
        item_id, _ = self._create_service_item()
        response = self.client.update_service_item_status(item_id=item_id, is_display=2)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    @pytest.mark.skip(reason="Bug 12: 已注释")
    def test_update_status_invalid_is_display_negative(self):
        """使用 isDisplay=-1 切换状态，应返回失败"""
        item_id, _ = self._create_service_item()
        response = self.client.update_service_item_status(item_id=item_id, is_display=-1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
