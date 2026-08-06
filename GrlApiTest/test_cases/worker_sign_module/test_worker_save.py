"""
test_worker_save.py - Worker user registration save API tests
=============================================================
Tests for the worker-save endpoint in the super individual worker sign module,
covering user creation, missing required fields, and invalid data."""

import time
import random

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
@pytest.mark.smoke
class TestWorkerSave(TestBase):
    def test_worker_save_success(self):
        """Create a worker user with valid params, should succeed"""
        user_uuid = f"worker-{int(time.time())}"
        phone = self._unique_phone()

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
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_save_invalid_phone_format(self):
        """Use invalid phone format, should fail"""
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone="12345",
            cert_num="110101199001011234",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_invalid_cert_num(self):
        """Use invalid cert number, should fail"""
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone=self._unique_phone(),
            cert_num="123456",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_empty_payload(self):
        """Empty payload, should fail or return error"""
        response = self.client.worker_save(
            name="",
            phone="",
            cert_num="",
            cert_front_photo="",
            cert_back_photo="",
            address="",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_missing_name(self):
        """Missing name field, should fail"""
        response = self.client.worker_save(
            name="",
            phone=self._unique_phone(),
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_missing_phone(self):
        """Missing phone field, should fail"""
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone="",
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_missing_cert_num(self):
        """Missing certNum field, should fail"""
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone=self._unique_phone(),
            cert_num="",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_missing_cert_photos(self):
        """Missing cert photos, should fail"""
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone=self._unique_phone(),
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="",
            cert_back_photo="",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_name_too_long(self):
        """Name exceeds 20 characters, should fail"""
        response = self.client.worker_save(
            name="A" * 21,
            phone=self._unique_phone(),
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_name_special_chars(self):
        """Name contains special characters, should fail"""
        response = self.client.worker_save(
            name="Test@#$%^&*",
            phone=self._unique_phone(),
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_cert_num_too_short(self):
        """certNum too short (less than 18 digits), should fail"""
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone=self._unique_phone(),
            cert_num="1101011990010112",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_save_duplicate_phone(self):
        """Duplicate phone number, should fail"""
        phone = self._unique_phone()
        self.client.worker_save(
            name=self._unique_real_name(),
            phone=phone,
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        response = self.client.worker_save(
            name=self._unique_real_name(),
            phone=phone,
            cert_num=f"11010119900101{random.randint(1000, 9999)}",
            cert_front_photo="/tmp/cert_front.jpg",
            cert_back_photo="/tmp/cert_back.jpg",
            address="Beijing",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)