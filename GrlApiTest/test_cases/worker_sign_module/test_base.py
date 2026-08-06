"""
test_base.py - Base test class for worker_sign_module
=====================================================
Provides common setup, login, and helper methods for the super individual worker sign module tests."""

import time
import random

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "worker_sign_module"
    _module_desc = "Super individual worker sign module"

    def _unique_real_name(self):
        """Generate a unique real name for test users"""
        return f"TestUser{int(time.time())}"

    def _unique_user_name(self):
        """Generate a unique username starting with 174 (11-digit phone)"""
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    def _unique_phone(self):
        """Generate a unique phone number starting with 174"""
        suffix = random.randint(10000000, 99999999)
        return f"174{suffix}"

    def _create_worker_user(self, user_uuid=None, phone=None):
        """Create a worker user via worker-save API

        Returns:
            (client_uuid, backend_uuid, phone) tuple
            client_uuid: 客户端生成的 user_uuid
            backend_uuid: 后端生成的 userUuid（UUID 格式），用于后续接口调用
            phone: 手机号
        """
        user_uuid = user_uuid or f"worker-{int(time.time())}"
        phone = phone or self._unique_phone()

        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone=phone,
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing, Dongcheng District",
            nation="Han",
            sex=1,
            birth="1990-01-01",
            user_uuid=user_uuid,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        backend_uuid = data.get("data", {}).get("userUuid", user_uuid)
        return user_uuid, backend_uuid, phone

    def _create_worker_sign(self, user_uuid=None, worker_phone=None):
        """Create a worker sign record via worker-sign/save API

        Returns:
            (sign_id, user_uuid) 元组

        如果未指定 user_uuid，先通过 worker_save 创建工人用户，
        使用后端生成的 UUID 参与入驻签署，确保 userUuid 格式合法。
        """
        if user_uuid is None:
            _, user_uuid, phone = self._create_worker_user()
            worker_phone = worker_phone or phone
        else:
            worker_phone = worker_phone or self._unique_phone()

        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=worker_phone,
            station_info_id=1,
            station_info_name="Test Station",
            province_area_code="110119000000",
            city_area_code="110119000000",
            district_area_code="110119000000",
            source_type=1,
            service_items=[
                {
                    "serviceItemId": 1,
                    "itemName": "Test Service",
                    "billingMethod": 1,
                    "amount": 100.0,
                }
            ],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        sign_id = data.get("data", {}).get("id")
        return sign_id, user_uuid

    def _delete_test_data(self, item_id):
        """Delete test data - no-op for worker sign module"""
        pass