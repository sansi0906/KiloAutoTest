"""
test_tax_type_config.py - 税种配置管理接口测试
============================================
覆盖税种配置管理模块的接口场景：
1. 新增税种配置
2. 分页查询税种配置
3. 编辑税种配置
4. 启用/禁用税种配置
5. 存在性校验（不存在的记录）
6. 输入校验（空名称、非法 fixedDisplay）
"""

import time

import pytest

from .test_base import TestBase


class TestTaxTypeConfig(TestBase):
    @pytest.mark.smoke
    def test_add_tax_type_success(self):
        """使用标准参数新增税种，应返回成功"""
        payload = self._build_tax_type_payload()
        response = self.client.add_tax_type_config(
            tax_type_name=payload["taxTypeName"],
            fixed_display=payload["fixedDisplay"],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 通过分页查询获取税种ID
        page_resp = self.client.page_tax_type_configs(page_num=1, page_size=10, tax_type_name=payload["taxTypeName"])
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        config_id = None
        for record in records:
            if record.get("taxTypeName") == payload["taxTypeName"]:
                config_id = record.get("id")
                break
        assert config_id, f"Created tax type not found in page results"

        # 验证数据库中的数据
        db_record = self._verify_tax_type_in_db(
            config_id=config_id,
            tax_type_name=payload["taxTypeName"],
            fixed_display=payload["fixedDisplay"],
        )
        assert db_record["status"] == 1, f"默认状态应为启用: {db_record['status']}"
        print(f"数据库验证成功: id={db_record['id']}, name={db_record['tax_type_name']}")

    def test_add_tax_type_missing_name(self):
        """缺少 taxTypeName，应返回失败"""
        response = self.client.add_tax_type_config(
            tax_type_name="",
            fixed_display=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_add_tax_type_duplicate_name(self):
        """使用重复的税种名称新增，应返回失败"""
        payload = self._build_tax_type_payload()
        response = self.client.add_tax_type_config(
            tax_type_name=payload["taxTypeName"],
            fixed_display=payload["fixedDisplay"],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 再次使用相同名称新增
        response2 = self.client.add_tax_type_config(
            tax_type_name=payload["taxTypeName"],
            fixed_display=payload["fixedDisplay"],
        )
        self.validator.assert_status_code(response2, 200)
        data2 = response2.json()
        self.assert_save_failure(data2)

    def test_page_tax_types_success(self):
        """正常分页查询税种配置，应返回成功"""
        response = self.client.page_tax_type_configs(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"
        page_data = data.get("data", {})
        assert "records" in page_data, "Missing records in page data"
        assert "total" in page_data, "Missing total in page data"

    def test_page_tax_types_by_name(self):
        """按税种名称模糊查询税种配置"""
        config_id, tax_type_name = self._save_and_get_id()

        response = self.client.page_tax_type_configs(page_num=1, page_size=10, tax_type_name=tax_type_name)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("taxTypeName") == tax_type_name for record in records)
        assert found, f"Created tax type '{tax_type_name}' not found in page results"

    def test_page_tax_types_by_status(self):
        """按状态查询税种配置"""
        config_id, tax_type_name = self._save_and_get_id()

        response = self.client.page_tax_type_configs(page_num=1, page_size=100, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("id") == config_id for record in records)
        assert found, f"Created tax type '{tax_type_name}' not found when filtering by status=1"

    def test_edit_tax_type_success(self):
        """编辑已存在的税种配置，应返回成功"""
        config_id, tax_type_name = self._save_and_get_id()
        new_tax_type_name = f"TestTax_EDIT{int(time.time())}"

        response = self.client.edit_tax_type_config(
            config_id=config_id,
            tax_type_name=new_tax_type_name,
            fixed_display=0,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证数据库中的数据
        db_record = self._verify_tax_type_in_db(
            config_id=config_id,
            tax_type_name=new_tax_type_name,
            fixed_display=0,
        )
        assert db_record["tax_type_name"] == new_tax_type_name, f"税种名称未更新: {db_record['tax_type_name']} != {new_tax_type_name}"
        print(f"编辑后数据库验证成功: id={db_record['id']}, name={db_record['tax_type_name']}")

    def test_edit_tax_type_non_existing(self):
        """编辑不存在的税种配置，应返回失败"""
        response = self.client.edit_tax_type_config(
            config_id=999999,
            tax_type_name="TestTax",
            fixed_display=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_tax_type_missing_name(self):
        """编辑税种配置缺少 taxTypeName，应返回失败"""
        config_id, _ = self._save_and_get_id()

        response = self.client.edit_tax_type_config(
            config_id=config_id,
            tax_type_name="",
            fixed_display=1,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_disable(self):
        """禁用已启用的税种配置，应返回成功"""
        config_id, _ = self._save_and_get_id()

        response = self.client.change_tax_type_status(config_id=config_id, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_enable(self):
        """启用已禁用的税种配置，应返回成功"""
        config_id, _ = self._save_and_get_id()

        # 先禁用
        self.client.change_tax_type_status(config_id=config_id, status=0)

        # 再启用
        response = self.client.change_tax_type_status(config_id=config_id, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_non_existing(self):
        """修改不存在的税种配置状态，应返回失败"""
        response = self.client.change_tax_type_status(config_id=999999, status=1)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_invalid_value(self):
        """修改税种配置状态为非法值，应返回失败"""
        config_id, _ = self._save_and_get_id()

        response = self.client.change_tax_type_status(config_id=config_id, status=2)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
