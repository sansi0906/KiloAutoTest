"""
test_base.py - 税种配置管理模块测试基类
==================================================
提供税种配置管理模块的通用测试设置和辅助方法
"""

import random
import time

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "tax_type_config_module"
    _module_desc = "税种配置管理模块"

    def _unique_tax_type_name(self):
        """生成唯一的税种名称（时间戳 + 随机数，避免秒级碰撞）"""
        return f"TestTax{int(time.time())}{random.randint(1000, 9999)}"

    def _build_tax_type_payload(self, tax_type_name=None, fixed_display=1, **kwargs):
        """构建税种新增/编辑标准入参"""
        payload = {
            "taxTypeName": tax_type_name or self._unique_tax_type_name(),
            "fixedDisplay": fixed_display,
        }
        payload.update(kwargs)
        return payload

    def _save_and_get_id(self, tax_type_name=None, fixed_display=1):
        """新增税种并通过分页查询获取ID

        Returns:
            (config_id, tax_type_name) 元组
        """
        payload = self._build_tax_type_payload(tax_type_name=tax_type_name, fixed_display=fixed_display)
        return self._create_and_get_id(
            create_fn=lambda: self.client.add_tax_type_config(
                tax_type_name=payload["taxTypeName"],
                fixed_display=payload["fixedDisplay"],
            ),
            query_fn=lambda: self.client.page_tax_type_configs(page_num=1, page_size=10, tax_type_name=payload["taxTypeName"]),
            match_key="taxTypeName",
            match_value=payload["taxTypeName"],
        )

    def _delete_test_data(self, item_id):
        """删除测试数据（通过 PostgreSQL 直接标记 delete_status）"""
        pg_helper = self._get_pg_helper()
        sql = "UPDATE cjgt_tax_type_config SET delete_status = 1 WHERE id = %s"
        try:
            pg_helper.execute(sql, (item_id,))
        except Exception as e:
            import logging
            logging.warning(f"Failed to delete tax type config id={item_id}: {e}")

    def _verify_tax_type_in_db(self, config_id, tax_type_name, fixed_display, pg_helper=None):
        """验证税种配置是否存在于 PostgreSQL 数据库

        Args:
            config_id: 税种配置ID
            tax_type_name: 税种名称
            fixed_display: 固定展示 (1-是, 0-否)
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            dict: 数据库记录
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, tax_type_name, fixed_display, status, delete_status
            FROM cjgt_tax_type_config
            WHERE id = %s AND tax_type_name = %s AND delete_status = 0
        """
        result = pg_helper.fetch_one(sql, (config_id, tax_type_name))
        assert result, f"税种配置在数据库中未找到: id={config_id}, name={tax_type_name}"

        assert result["tax_type_name"] == tax_type_name, f"税种名称不匹配: {result['tax_type_name']} != {tax_type_name}"
        assert result["fixed_display"] == fixed_display, f"固定展示不匹配: {result['fixed_display']} != {fixed_display}"
        assert result["status"] == 1, f"默认状态应为启用: {result['status']}"

        return result

    def _verify_tax_type_deleted(self, config_id, pg_helper=None):
        """验证税种配置已删除（delete_status != 0）

        Args:
            config_id: 税种配置ID
            pg_helper: PostgreSQL 数据库助手实例

        Returns:
            bool: 是否已删除
        """
        pg_helper = pg_helper or self._get_pg_helper()

        sql = """
            SELECT id, delete_status FROM cjgt_tax_type_config
            WHERE id = %s
        """
        result = pg_helper.fetch_one(sql, (config_id,))
        if result:
            return result.get("delete_status", 0) != 0
        return True
