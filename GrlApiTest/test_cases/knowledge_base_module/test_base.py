"""
test_base.py - 知识库管理模块测试基类
===================================================
提供知识库管理模块的通用测试设置和辅助方法
"""

import time

import pytest
from utils.base_test import BaseTest


class TestBase(BaseTest):
    _module_name = "knowledge_base_module"
    _module_desc = "知识库管理模块"

    def _unique_title(self):
        """生成唯一的标题"""
        return f"TestKB{int(time.time())}"

    def _build_knowledge_payload(self, title=None, content=None, consult_type=1, display_position=None, applicable_area=None, **kwargs):
        """构建知识库新增/编辑标准入参"""
        payload = {
            "title": title or self._unique_title(),
            "content": content or "TestContent",
            "consultType": consult_type,
            "displayPosition": display_position if display_position is not None else [0, 1],
            "applicableArea": applicable_area if applicable_area is not None else [
                {"code": "110119000000", "name": "延庆区", "level": "county"}
            ],
        }
        payload.update(kwargs)
        return payload

    def _save_and_get_id(self, **kwargs):
        """新增知识库并通过分页查询获取ID"""
        payload = self._build_knowledge_payload(**kwargs)
        response = self.client.save_knowledge(
            title=payload["title"],
            content=payload["content"],
            consult_type=payload["consultType"],
            display_position=payload["displayPosition"],
            applicable_area=payload["applicableArea"],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

        page_resp = self.client.page_knowledge(page_num=1, page_size=10, title=payload["title"])
        self.validator.assert_status_code(page_resp, 200)
        page_data = page_resp.json()
        records = page_data.get("data", {}).get("records", [])
        knowledge_id = None
        for record in records:
            if record.get("title") == payload["title"]:
                knowledge_id = record.get("id")
                break
        assert knowledge_id, f"Knowledge base not found after creation: {page_data}"
        self._created_ids.append(knowledge_id)
        self._log_test_data_created(knowledge_id, payload["title"])
        return knowledge_id, payload["title"]

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.delete_knowledge(knowledge_id=item_id)
