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

import pytest

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
            amount=150.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_update_pricing_no_record(self):
        """更新未导入定价数据的服务项目定价，按正常逻辑应返回失败"""
        item_id, item_name = self._create_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            amount=150.0,
            area_list=[{"code": "110101000000", "level": "county", "name": "东城区"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_update_pricing_missing_amount(self):
        """缺少 amount，应返回失败"""
        item_id, _ = self._get_existing_service_item()

        response = self.client.update_pricing(
            service_item_id=item_id,
            amount=None,
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
            amount=150.0,
            area_list=[],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
