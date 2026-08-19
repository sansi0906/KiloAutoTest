"""
test_contract.py - 合同分页查询接口测试
=============================================
覆盖合同管理模块的查询场景：
- 正常分页查询合同
- 按合同编号查询
- 按甲方名称查询
- 无效页码
- 超大每页条数
"""

import pytest

from .test_base import TestBase


@pytest.mark.skip(reason="暂不执行：contract 表/接口待确认")
class TestContract(TestBase):
    def test_page_contracts_success(self):
        """正常分页查询合同列表，应返回成功"""

        response = self.client.page_contracts(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page contracts failed: {data}"
        assert "data" in data
        assert "records" in data["data"]
        assert "total" in data["data"]

    def test_page_contracts_by_contact_no(self):
        """按合同编号模糊查询，应返回成功"""

        response = self.client.page_contracts(page_num=1, page_size=10, contact_no="HT")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page contracts by contact no failed: {data}"

    def test_page_contracts_by_party_a_name(self):
        """按甲方名称查询，应返回成功"""

        response = self.client.page_contracts(page_num=1, page_size=10, party_a_name="测试")
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in ("0", "00"), f"Page contracts by party A name failed: {data}"

    def test_page_contracts_invalid_page_num(self):
        """无效页码（0），应返回失败"""

        response = self.client.page_contracts(page_num=0, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"

    def test_page_contracts_large_page_size(self):
        """超大每页条数（1000），应返回失败"""

        response = self.client.page_contracts(page_num=1, page_size=1000)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") not in ("0", "00"), f"Expected failure but got success: {data}"
