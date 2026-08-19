"""
test_base.py - 合同服务配置管理模块测试基类
==================================================
提供合同服务配置管理模块的通用测试设置和辅助方法
合同服务配置与服务项目配置为 1:1 关联关系
"""

import time
import random

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "contract_service_config_module"
    _module_desc = "合同服务配置管理模块"

    def _unique_title(self):
        """生成唯一的合同配置标题"""
        return f"合同配置{int(time.time())}"

    def _create_service_item(self, item_name=None):
        """创建服务项目（用于1:1关联测试）

        Returns:
            (item_id, item_name) 元组
        """
        item_name = item_name or f"Test{random.randint(1000, 9999)}"
        return self._create_and_get_id(
            create_fn=lambda: self.client.add_service_item(
                item_name=item_name,
                billing_method=1,
                subtitle="TestSubtitle",
                item_desc="TestDescription",
            ),
            query_fn=lambda: self.client.page_service_items(page_num=1, page_size=10, item_name=item_name),
            match_key="itemName",
            match_value=item_name,
        )

    def _create_contact_config(self, service_item_id, title=None, content=None, price_content=None):
        """创建合同配置（合同服务配置）并通过分页查询获取配置ID

        Returns:
            (config_id, title) 元组
        """
        title = title or self._unique_title()
        content = content or "测试内容"
        price_content = price_content or "价格内容"
        config_id = self._create_and_get_id(
            create_fn=lambda: self.client.save_contact_config(
                service_item_id=service_item_id,
                title=title,
                content=content,
                price_content=price_content,
            ),
            query_fn=lambda: self.client.page_contact_configs(page_num=1, page_size=10, service_item_id=service_item_id),
            match_key="serviceItemId",
            match_value=service_item_id,
        )[0]
        return config_id, title

    def _delete_test_data(self, item_id):
        """删除测试数据（合同配置）"""
        self.client.delete_contact_config(config_id=item_id)

    def _verify_contact_config_in_db(self, config_id, title, service_item_id, pg_helper=None):
        """验证合同配置是否存在于 PostgreSQL 数据库

        Args:
            config_id: 合同配置ID
            title: 合同配置标题
            service_item_id: 服务项目ID
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 数据库记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, title, content, service_item_id, delete_status, type, price_content
            FROM cjgt_contact_config
            WHERE id = %s AND title = %s AND service_item_id = %s AND delete_status = 0
        """
        result = pg_helper.fetch_one(sql, (config_id, title, service_item_id))
        assert result, f"合同配置在数据库中未找到: id={config_id}, title={title}, service_item_id={service_item_id}"
        return result

    def _verify_contact_config_deleted(self, config_id, pg_helper=None):
        """验证合同配置已删除（delete_status != 0）

        Args:
            config_id: 合同配置ID
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            bool: 是否已删除
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, delete_status FROM cjgt_contact_config
            WHERE id = %s
        """
        result = pg_helper.fetch_one(sql, (config_id,))
        if result:
            return result.get("delete_status", 0) != 0
        return True
