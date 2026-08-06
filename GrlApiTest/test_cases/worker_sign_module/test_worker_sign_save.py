"""
test_worker_sign_save.py - Worker sign save API tests
=======================================================
Tests for the worker-sign/save endpoint (super individual worker onboarding)."""

import time
import random

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
@pytest.mark.smoke
class TestWorkerSignSave(TestBase):
    def test_worker_sign_save_success(self):
        """Create a worker sign record with valid params, should succeed"""
        # 先创建工人用户，获取后端生成的 userUuid
        _, user_uuid, phone = self._create_worker_user()

        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
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
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_sign_save_missing_user_uuid(self):
        """Missing userUuid field, should fail"""
        response = self.client.worker_sign_save(
            user_uuid="",
            worker_phone=self._unique_phone(),
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
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_worker_phone(self):
        """Missing workerPhone field, should fail"""
        response = self.client.worker_sign_save(
            user_uuid=f"worker-{int(time.time())}",
            worker_phone="",
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
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_station_info_id(self):
        """Missing stationInfoId field, should fail"""
        response = self.client.worker_sign_save(
            user_uuid=f"worker-{int(time.time())}",
            worker_phone=self._unique_phone(),
            station_info_id=None,
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
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_service_items(self):
        """Missing serviceItems field, should fail"""
        response = self.client.worker_sign_save(
            user_uuid=f"worker-{int(time.time())}",
            worker_phone=self._unique_phone(),
            station_info_id=1,
            station_info_name="Test Station",
            province_area_code="110119000000",
            city_area_code="110119000000",
            district_area_code="110119000000",
            source_type=1,
            service_items=[],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_sign_save_invalid_phone_format(self):
        """Use invalid phone format, should fail"""
        response = self.client.worker_sign_save(
            user_uuid=f"worker-{int(time.time())}",
            worker_phone="12345",
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
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_all_required_fields(self):
        """All required fields empty, should fail"""
        response = self.client.worker_sign_save(
            user_uuid="",
            worker_phone="",
            station_info_id=None,
            station_info_name="",
            province_area_code="",
            city_area_code="",
            district_area_code="",
            source_type=None,
            service_items=[],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_station_info_name(self):
        """Missing stationInfoName field, should fail"""
        _, user_uuid, phone = self._create_worker_user()
        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
            station_info_id=1,
            station_info_name="",
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
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_area_codes(self):
        """Missing area code fields, should fail"""
        _, user_uuid, phone = self._create_worker_user()
        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
            station_info_id=1,
            station_info_name="Test Station",
            province_area_code="",
            city_area_code="",
            district_area_code="",
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
        self.assert_save_failure(data)

    def test_worker_sign_save_invalid_station_info_id(self):
        """Invalid/nonexistent stationInfoId, should fail"""
        _, user_uuid, phone = self._create_worker_user()
        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
            station_info_id=999999,
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
        self.assert_save_failure(data)

    def test_worker_sign_save_invalid_service_item_id(self):
        """Invalid/nonexistent serviceItemId, should fail"""
        _, user_uuid, phone = self._create_worker_user()
        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
            station_info_id=1,
            station_info_name="Test Station",
            province_area_code="110119000000",
            city_area_code="110119000000",
            district_area_code="110119000000",
            source_type=1,
            service_items=[
                {
                    "serviceItemId": 999999,
                    "itemName": "Test Service",
                    "billingMethod": 1,
                    "amount": 100.0,
                }
            ],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_sign_save_negative_amount(self):
        """Negative amount in service_items, should fail"""
        _, user_uuid, phone = self._create_worker_user()
        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
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
                    "amount": -100.0,
                }
            ],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_sign_save_missing_service_item_fields(self):
        """Missing serviceItem fields (itemName, billingMethod, amount), should fail"""
        _, user_uuid, phone = self._create_worker_user()
        response = self.client.worker_sign_save(
            user_uuid=user_uuid,
            worker_phone=phone,
            station_info_id=1,
            station_info_name="Test Station",
            province_area_code="110119000000",
            city_area_code="110119000000",
            district_area_code="110119000000",
            source_type=1,
            service_items=[
                {
                    "serviceItemId": 1,
                }
            ],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)