"""
test_contact_config.py - 合同配置（合同服务配置）接口测试
=============================================
覆盖合同配置管理模块的接口场景，验证与服务项目的 1:1 关联关系：
- 正常创建合同配置（关联服务项目）
- 缺少必填字段（serviceItemId/title）
- 空标题
- 无效服务项目ID
- 重复创建（1:1关系验证）
- 分页查询合同配置
- 编辑合同配置
- 删除合同配置
- 查询合同配置详情
"""

import pytest

from .test_base import TestBase


class TestContactConfig(TestBase):
    @pytest.mark.smoke
    def test_save_contact_config_success(self):
        """使用有效参数创建合同配置（关联服务项目），应返回成功"""

        service_item_id, _ = self._create_service_item()
        title = self._unique_title()

        response = self.client.save_contact_config(
            service_item_id=service_item_id,
            title=title,
            content="测试内容",
            price_content="价格内容",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证合同配置与服务项目1:1关联
        page_resp = self.client.page_contact_configs(page_num=1, page_size=10, service_item_id=service_item_id)
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        assert len(records) == 1, f"Expected 1 contact config for service item, got {len(records)}"
        assert records[0].get("serviceItemId") == service_item_id
        assert records[0].get("title") == title

        # 验证数据库中的数据
        config_id = records[0].get("id")
        db_record = self._verify_contact_config_in_db(config_id, title, service_item_id)
        assert db_record["content"] == "测试内容", f"content 未保存成功: {db_record}"
        assert db_record["price_content"] == "价格内容", f"price_content 未保存成功: {db_record}"
        print(f"数据库验证成功: id={db_record['id']}, title={db_record['title']}, service_item_id={db_record['service_item_id']}")

    def test_save_contact_config_missing_service_item_id(self):
        """缺少 serviceItemId，应返回失败"""

        response = self.client.save_contact_config(
            service_item_id=None,
            title=self._unique_title(),
            content="测试内容",
            price_content="价格内容",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_contact_config_missing_title(self):
        """缺少 title，应返回失败"""

        service_item_id, _ = self._create_service_item()
        response = self.client.save_contact_config(
            service_item_id=service_item_id,
            title="",
            content="测试内容",
            price_content="价格内容",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_contact_config_missing_content(self):
        """缺少 content 必填字段，应返回失败"""

        service_item_id, _ = self._create_service_item()
        response = self.client.save_contact_config(
            service_item_id=service_item_id,
            title=self._unique_title(),
            content=None,
            price_content="价格内容",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_contact_config_missing_price_content(self):
        """缺少 priceContent 必填字段，应返回失败"""

        service_item_id, _ = self._create_service_item()
        response = self.client.save_contact_config(
            service_item_id=service_item_id,
            title=self._unique_title(),
            content="测试内容",
            price_content=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_contact_config_invalid_service_item_id(self):
        """无效服务项目ID，应返回失败"""

        response = self.client.save_contact_config(
            service_item_id=999999,
            title=self._unique_title(),
            content="测试内容",
            price_content="价格内容",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_contact_config_duplicate_1to1(self):
        """同一服务项目创建多个合同配置（违反1:1关系），应返回失败"""

        service_item_id, _ = self._create_service_item()
        title_1 = self._unique_title()
        title_2 = self._unique_title()

        response_1 = self.client.save_contact_config(
            service_item_id=service_item_id,
            title=title_1,
            content="测试内容1",
            price_content="价格内容1",
        )
        self.validator.assert_status_code(response_1, 200)
        data_1 = response_1.json()
        self.assert_save_success(data_1)

        response_2 = self.client.save_contact_config(
            service_item_id=service_item_id,
            title=title_2,
            content="测试内容2",
            price_content="价格内容2",
        )
        self.validator.assert_status_code(response_2, 200)
        data_2 = response_2.json()
        self.assert_save_failure(data_2)

    def test_page_contact_configs_success(self):
        """正常分页查询合同配置，应返回成功"""

        service_item_id, _ = self._create_service_item()
        self._create_contact_config(service_item_id=service_item_id)

        response = self.client.page_contact_configs(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page contact configs failed: {data}"
        assert "data" in data
        assert "records" in data["data"]
        assert "total" in data["data"]

    def test_page_contact_configs_by_service_item_id(self):
        """按服务项目ID查询合同配置，应返回成功"""

        service_item_id, _ = self._create_service_item()
        self._create_contact_config(service_item_id=service_item_id)

        response = self.client.page_contact_configs(page_num=1, page_size=10, service_item_id=service_item_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page by service item failed: {data}"
        assert len(data.get("data", {}).get("records", [])) >= 1

    def test_get_contact_config_detail_existing(self):
        """查询已存在的合同配置详情，应返回成功"""

        service_item_id, _ = self._create_service_item()
        config_id, title = self._create_contact_config(service_item_id=service_item_id)

        response = self.client.get_contact_config_detail(config_id=config_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Get detail failed: {data}"
        assert data["data"]["id"] == config_id
        assert data["data"]["title"] == title

    def test_get_contact_config_detail_non_existing(self):
        """查询不存在的合同配置ID，应返回失败"""

        response = self.client.get_contact_config_detail(config_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_edit_contact_config_success(self):
        """正常编辑合同配置，应返回成功"""

        service_item_id, _ = self._create_service_item()
        config_id, title = self._create_contact_config(service_item_id=service_item_id)

        new_title = f"{title}_edited"
        response = self.client.edit_contact_config(
            config_id=config_id,
            service_item_id=service_item_id,
            title=new_title,
            content="更新后的内容",
            price_content="更新后的价格",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证编辑生效（API 返回）
        detail_resp = self.client.get_contact_config_detail(config_id=config_id)
        detail_data = detail_resp.json()
        assert detail_data["data"]["title"] == new_title

        # 验证数据库中数据是否与入参一致
        db_record = self._verify_contact_config_in_db(config_id, new_title, service_item_id)
        assert db_record["content"] == "更新后的内容", f"content 未更新: {db_record}"
        assert db_record["price_content"] == "更新后的价格", f"price_content 未更新: {db_record}"
        print(f"数据库验证成功: id={db_record['id']}, title={db_record['title']}, service_item_id={db_record['service_item_id']}")

    def test_edit_contact_config_not_exist(self):
        """编辑不存在的合同配置，应返回失败"""

        response = self.client.edit_contact_config(
            config_id=999999,
            service_item_id=1,
            title="测试",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_delete_contact_config_success(self):
        """正常删除合同配置，应返回成功"""

        service_item_id, _ = self._create_service_item()
        config_id, _ = self._create_contact_config(service_item_id=service_item_id)

        response = self.client.delete_contact_config(config_id=config_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        # 验证删除后查询详情失败
        detail_resp = self.client.get_contact_config_detail(config_id=config_id)
        detail_data = detail_resp.json()
        assert detail_data.get("code") not in ("0", "00"), f"Expected not found but got: {detail_data}"

        # 验证数据库中 delete_status 已改变
        is_deleted = self._verify_contact_config_deleted(config_id)
        assert is_deleted, f"合同配置未标记为删除: id={config_id}"
        print(f"数据库删除验证成功: id={config_id}, delete_status 已改变")

    def test_delete_contact_config_non_existing(self):
        """删除不存在的合同配置，应返回失败"""

        response = self.client.delete_contact_config(config_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
