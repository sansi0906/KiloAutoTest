"""
test_gongrenle_info.py - Gongrenle worker info query API tests
===============================================================
Tests for the gongrenle-info endpoint in the super individual worker sign module."""

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
class TestGongrenleInfo(TestBase):
    def test_gongrenle_info_success(self):
        """Query gongrenle worker info using valid phone, should succeed"""
        response = self.client.gongrenle_info(phone="13800138000")
        self.validator.assert_status_code(response, 200)
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_gongrenle_info_nonexistent_phone(self):
        """Query gongrenle worker info using nonexistent phone, should succeed"""
        response = self.client.gongrenle_info(phone="19999999999")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)