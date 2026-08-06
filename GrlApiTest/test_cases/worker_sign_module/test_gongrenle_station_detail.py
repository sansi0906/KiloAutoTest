"""
test_gongrenle_station_detail.py - Gongrenle station detail query API tests
============================================================================
Tests for the gongrenle-station-detail endpoint in the super individual worker sign module."""

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
class TestGongrenleStationDetail(TestBase):
    def test_station_detail_success(self):
        """Query station detail using valid businessId, should succeed"""
        response = self.client.gongrenle_station_detail(business_id=1)
        self.validator.assert_status_code(response, 200)
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_station_detail_invalid_business_id(self):
        """Query station detail using nonexistent businessId, should succeed"""
        response = self.client.gongrenle_station_detail(business_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)