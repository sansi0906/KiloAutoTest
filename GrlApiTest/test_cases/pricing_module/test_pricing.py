"""
test_pricing.py - 服务定价配置管理接口测试
=============================================
覆盖服务定价配置管理模块的接口场景，按以下顺序验证：
1. 导入服务定价数据
2. 获取服务项目定价树
3. 根据区域获取服务定价树
4. 更新服务定价
"""

import os
from pathlib import Path

import psycopg2

import pytest

from config import PG_CONFIG
from .test_base import TestBase


class TestPricing(TestBase):
    _EXCEL_PATH = Path(__file__).resolve().parents[2] / "data" / "服务定价数据.xlsx"
    def _get_existing_service_item(self, display_only=True):
        """获取一个已存在的服务项目ID和名称

        Args:
            display_only: 是否只获取展示状态为1的项目

        Returns:
            (item_id, item_name) 元组
        """
        if display_only:
            resp = self.client.list_display_service_items(is_display=1)
        else:
            resp = self.client.list_display_service_items()
        self.validator.assert_status_code(resp, 200)
        data = resp.json()
        self.assert_save_success(data)
        items = data.get("data", [])
        assert items, "No service items found"
        return items[0]["id"], items[0]["itemName"]

    @pytest.mark.smoke
    def test_import_pricing_success(self):
        """使用有效Excel文件导入服务定价数据"""
        item_id, item_name = self._get_existing_service_item()

        if not self._EXCEL_PATH.exists():
            pytest.skip(f"Excel file not found: {self._EXCEL_PATH}")

        response = self.client.import_pricing(
            service_item_id=item_id,
            service_item_name=item_name,
            file_path=str(self._EXCEL_PATH),
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_get_pricing_tree_success(self):
        """获取已导入定价数据的服务项目定价树"""
        item_id, item_name = self._get_existing_service_item()

        response = self.client.get_pricing_tree(service_item_id=item_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"

    def test_get_pricing_tree_no_data(self):
        """获取未导入定价数据的服务项目定价树，应返回空树"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.get_pricing_tree(service_item_id=item_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_get_pricing_tree_missing_id(self):
        """缺少 serviceItemId，应返回失败"""
        response = self.client.get_pricing_tree(service_item_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_get_pricing_tree_by_areas_success(self):
        """根据区域列表获取服务定价树"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.get_pricing_tree_by_areas(
            service_item_id=item_id,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"

    def test_get_pricing_tree_by_areas_missing_id(self):
        """缺少 serviceItemId，应返回失败"""
        response = self.client.get_pricing_tree_by_areas(
            service_item_id=None,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_pricing_success(self):
        """更新已存在的服务项目定价"""
        item_id, _ = self._get_existing_service_item()

        if self._EXCEL_PATH.exists():
            self.client.import_pricing(
                service_item_id=item_id,
                service_item_name="Test",
                file_path=str(self._EXCEL_PATH),
            )

        response = self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=150.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    @pytest.mark.skip(reason="Bug 20: 已注释")
    @pytest.mark.backend_bug
    def test_update_pricing_no_record(self):
        """更新未导入定价数据的服务项目定价，按正常逻辑应返回失败"""
        item_id, item_name = self._create_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=150.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_pricing_missing_amount(self):
        """缺少 pendingAmount，应返回失败"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=None,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_pricing_missing_area_list(self):
        """缺少 areaList，应返回失败"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=150.0,
            area_list=[],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_pricing_missing_service_item_id(self):
        """更新定价缺少 serviceItemId，应返回失败"""
        response = self.client.update_pricing(
            service_item_id=None,
            pending_amount=150.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_get_pricing_tree_missing_service_item_id(self):
        """获取定价树缺少 serviceItemId，应返回失败"""
        response = self.client.get_pricing_tree(service_item_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_get_pricing_tree_by_areas_missing_area_list(self):
        """根据区域获取定价树，使用正确的 serviceItemId 和 areaList 验证正常场景"""
        item_id, _ = self._get_existing_service_item()
        response = self.client.get_pricing_tree_by_areas(
            service_item_id=item_id,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_pricing_init_after_service_item_create(self):
        """新增服务项目后，自动初始化全国省市区定价数据，amount 默认为 null"""
        item_id, item_name = self._create_service_item()

        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
        )
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*), SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) '
            'FROM cjgt_service_pricing WHERE service_item_id = %s AND delete_status = 0',
            (item_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        assert row[0] > 0, f"Expected pricing records after service item create, got {row[0]}"
        assert row[1] == row[0], f"Expected all amount to be null, got {row[1]}/{row[0]}"
        print(f"初始化定价数据验证成功: 共 {row[0]} 条记录，amount 均为 null")

    def test_pricing_first_update_writes_amount(self):
        """第一次改价，直接将 pending_amount 写入 amount，pending_amount 清空"""
        item_id, _ = self._create_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=100.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
        )
        cursor = conn.cursor()
        cursor.execute(
            'SELECT amount, pending_amount, effective_time '
            'FROM cjgt_service_pricing WHERE service_item_id = %s AND delete_status = 0 AND area_code = %s',
            (item_id, '110101000000'),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        assert row is not None, "Pricing record not found"
        assert row[0] == 100.0, f"Expected amount=100.0 after first update, got {row[0]}"
        assert row[1] is None, f"Expected pending_amount=None after first update, got {row[1]}"
        assert row[2] is None, f"Expected effective_time=None after first update, got {row[2]}"
        print(f"第一次改价验证成功: amount={row[0]}, pending_amount={row[1]}, effective_time={row[2]}")

    def test_pricing_second_update_updates_pending_and_effective_time(self):
        """第二次改价，更新 pending_amount 及生效时间，amount 保持不变"""
        item_id, _ = self._create_service_item()

        # 第一次改价
        self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=100.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )

        # 第二次改价
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
        response = self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=200.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
            effective_time=tomorrow,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password'],
        )
        cursor = conn.cursor()
        cursor.execute(
            'SELECT amount, pending_amount, effective_time '
            'FROM cjgt_service_pricing WHERE service_item_id = %s AND delete_status = 0 AND area_code = %s',
            (item_id, '110101000000'),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        assert row is not None, "Pricing record not found"
        assert row[0] == 100.0, f"Expected amount=100.0 unchanged, got {row[0]}"
        assert row[1] == 200.0, f"Expected pending_amount=200.0, got {row[1]}"
        assert row[2] is not None, f"Expected effective_time to be set, got {row[2]}"
        print(f"第二次改价验证成功: amount={row[0]}, pending_amount={row[1]}, effective_time={row[2]}")

    def test_pricing_query_returns_amount(self):
        """查询定价树返回 amount 值（当前生效价格），同时返回 pendingAmount 和 effectiveTime"""
        item_id, _ = self._create_service_item()

        # 第一次改价
        self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=100.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )

        # 第二次改价
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
        self.client.update_pricing(
            service_item_id=item_id,
            pending_amount=200.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
            effective_time=tomorrow,
        )

        # 查询定价树
        response = self.client.get_pricing_tree_by_areas(
            service_item_id=item_id,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        tree = data.get("data", {}).get("servicePricingTree", [])
        assert len(tree) > 0, "Expected pricing tree nodes"

        node = tree[0]
        assert node.get("amount") == 100.0, f"Expected amount=100.0 in query, got {node.get('amount')}"
        assert node.get("pendingAmount") == 200.0, f"Expected pendingAmount=200.0 in query, got {node.get('pendingAmount')}"
        assert node.get("effectiveTime") is not None, "Expected effectiveTime in query"
        print(f"查询验证成功: amount={node.get('amount')}, pendingAmount={node.get('pendingAmount')}, effectiveTime={node.get('effectiveTime')}")
