"""
test_base.py - 服务项目配置管理模块测试基类
==================================================
提供服务项目配置管理模块的通用测试设置和辅助方法
"""

import random

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "service_item_module"
    _module_desc = "服务项目配置管理模块"

    def _unique_item_name(self):
        """生成唯一的服务项目名称（最长10个字符）"""
        suffix = random.randint(1000, 9999)
        return f"Test{suffix}"

    def _delete_test_data(self, item_id):
        """删除测试数据（service_item 没有 delete 接口，这里只是占位）"""
        pass

    def _verify_service_item_in_db(self, item_id, item_name, pg_helper=None):
        """验证服务项目是否存在于 PostgreSQL 数据库

        Args:
            item_id: 服务项目ID
            item_name: 服务项目名称
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 数据库记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, item_name, subtitle, billing_method, item_desc, is_display, delete_status
            FROM cjgt_service_item
            WHERE id = %s AND item_name = %s AND delete_status = 0
        """
        result = pg_helper.fetch_one(sql, (item_id, item_name))
        assert result, f"服务项目在数据库中未找到: id={item_id}, name={item_name}"
        return result

    def _verify_pricing_initialized(self, service_item_id, pg_helper=None):
        """验证服务项目定价是否已初始化（所有省市区，amount为null）

        Args:
            service_item_id: 服务项目ID
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            list: 定价记录列表
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, area_code, area_name, level, amount
            FROM cjgt_service_pricing
            WHERE service_item_id = %s AND delete_status = 0
            ORDER BY level, area_code
        """
        records = pg_helper.fetch_all(sql, (service_item_id,))
        assert records, f"服务项目定价未初始化: service_item_id={service_item_id}"

        null_amount_records = [r for r in records if r.get("amount") is None]
        assert len(null_amount_records) == len(records), \
            f"存在非null amount的记录: {[r for r in records if r.get('amount') is not None]}"

        levels = set(r.get("level") for r in records)
        assert levels, f"定价记录缺少层级信息: {levels}"

        return records
