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
        return self._create_and_get_id(
            create_fn=lambda: self.client.save_knowledge(
                title=payload["title"],
                content=payload["content"],
                consult_type=payload["consultType"],
                display_position=payload["displayPosition"],
                applicable_area=payload["applicableArea"],
            ),
            query_fn=lambda: self.client.page_knowledge(page_num=1, page_size=10, title=payload["title"]),
            match_key="title",
            match_value=payload["title"],
        )

    def _delete_test_data(self, item_id):
        """删除测试数据"""
        self.client.delete_knowledge(knowledge_id=item_id)
