"""
test_worker_info.py - Worker info query API tests
===================================================
Tests for the worker-info endpoint in the super individual worker sign module."""

import time
import random

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
class TestWorkerInfo(TestBase):
    def test_worker_info_success_with_uuid(self):
        """Query worker info using userUuid, should succeed"""
        sign_id, user_uuid = self._create_worker_sign()

        response = self.client.worker_info(user_uuid=user_uuid)
        self.validator.assert_status_code(response, 200)
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_info_success_with_phone(self):
        """Query worker info using phone, should succeed"""
        sign_id, user_uuid = self._create_worker_sign()
        phone = self._unique_phone()

        response = self.client.worker_info(phone=phone)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_info_missing_params(self):
        """Query without any params, should fail with validation error"""
        response = self.client.worker_info()
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_worker_info_nonexistent_user(self):
        """Query with nonexistent userUuid, should succeed but return empty"""
        response = self.client.worker_info(user_uuid="nonexistent-uuid")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_info_invalid_user_uuid_format(self):
        """Invalid userUuid format (not a valid UUID), should fail or return empty"""
        response = self.client.worker_info(user_uuid="invalid-uuid-format")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # Should either fail or return empty data
        assert data.get("code") in ("0", "00", "03"), f"Unexpected response: {data}"