"""
test_gongrenle_station_list.py - Gongrenle station list query API tests
=========================================================================
Tests for the gongrenle-station-list endpoint in the super individual worker sign module."""

import time
import random

import pytest

from .test_base import TestBase


@pytest.mark.worker_sign
class TestGongrenleStationList(TestBase):
    def test_station_list_success_with_uuid(self):
        """Query station list using userUuid, should succeed"""
        user_uuid = f"worker-{int(time.time())}"

        response = self.client.gongrenle_station_list(user_uuid=user_uuid)
        self.validator.assert_status_code(response, 200)
        self.assert_response_time(response, max_duration_ms=500)
        data = response.json()
        self.assert_save_success(data)

    def test_station_list_success_with_name(self):
        """Query station list using name filter, should succeed"""
        response = self.client.gongrenle_station_list(name="Test Station")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_station_list_with_pagination(self):
        """Query station list with pagination params, should succeed"""
        response = self.client.gongrenle_station_list(page=1, limit=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_station_list_missing_params(self):
        """Query without any params, should succeed"""
        response = self.client.gongrenle_station_list()
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)