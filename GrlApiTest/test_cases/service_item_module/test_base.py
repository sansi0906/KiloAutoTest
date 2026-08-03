"""
test_base.py - 服务项目配置管理模块测试基类
===================================================
提供服务项目配置管理模块的通用测试设置和辅助方法
"""

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "service_item_module"
    _module_desc = "服务项目配置管理模块"

    def _unique_item_name(self):
        """生成唯一的服务项目名称（最长10个字符）"""
        import random
        suffix = random.randint(1000, 9999)
        return f"Test{suffix}"

    def _create_service_item(self, item_name=None, billing_method=1):
        """新增服务项目并通过分页查询获取项目ID

        Returns:
            (item_id, item_name) 元组
        """
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
        self._created_ids.append(item_id)
        self._log_test_data_created(item_id, item_name)
        return item_id, item_name

    def _delete_test_data(self, item_id):
        """删除测试数据（service_item 没有 delete 接口，这里只是占位）"""
        pass
