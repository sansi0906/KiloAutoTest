"""
test_worker_authorization.py - Worker authorization API tests
==============================================================
Tests for the worker-authorization endpoint in the super individual worker sign module."""

import time
import random

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
class TestWorkerAuthorization(TestBase):
    def test_worker_authorization_success(self):
        """Authorize worker user, should succeed"""
        sign_id, user_uuid = self._create_worker_sign()

        response = self.client.worker_authorization(user_uuid=user_uuid)
        self.validator.assert_status_code(response, 200)
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_authorization_with_phone(self):
        """Authorize worker using phone param, should succeed"""
        sign_id, user_uuid = self._create_worker_sign()
        phone = self._unique_phone()

        response = self.client.worker_authorization(phone=phone)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_worker_authorization_missing_params(self):
        """Authorize without any params, should fail with validation error"""
        response = self.client.worker_authorization()
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)