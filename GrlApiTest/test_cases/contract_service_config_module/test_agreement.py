"""
test_agreement.py - 协议管理接口测试
=============================================
覆盖协议管理模块的查询场景：
- 分页查询协议列表
- 查询协议详情
- 编辑协议
- 缺少ID查询详情
- 无效ID查询详情
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：agreement 表/接口待确认")
class TestAgreement(TestBase):
    def test_page_agreements_success(self):
        """正常分页查询协议列表，应返回成功"""

        response = self.client.page_agreements(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page agreements failed: {data}"
        assert "data" in data
        assert "records" in data["data"]
        assert "total" in data["data"]

    def test_get_agreement_detail_existing(self):
        """查询已存在的协议详情，应返回成功"""

        page_resp = self.client.page_agreements(page_num=1, page_size=1)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        if not records:
            pytest.skip("No existing agreements to test detail")

        agreement_id = records[0].get("id")
        response = self.client.get_agreement_detail(agreement_id=agreement_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Get agreement detail failed: {data}"
        assert "data" in data
        assert data["data"]["id"] == agreement_id

    def test_get_agreement_detail_non_existing(self):
        """查询不存在的协议详情，应返回失败"""

        response = self.client.get_agreement_detail(agreement_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_get_agreement_detail_missing_id(self):
        """缺少ID查询详情，应返回失败"""

        response = self.client.get_agreement_detail(agreement_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_edit_agreement_success(self):
        """正常编辑协议，应返回成功"""

        page_resp = self.client.page_agreements(page_num=1, page_size=1)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        if not records:
            pytest.skip("No existing agreements to test edit")

        agreement_id = records[0].get("id")
        response = self.client.edit_agreement(
            agreement_id=agreement_id,
            title="更新后的协议标题",
            content="更新后的协议内容",
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
