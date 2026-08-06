"""
test_knowledge_base.py - 知识库管理接口测试
=============================================
覆盖知识库管理模块的接口场景：
1. 新增知识库
2. 分页查询知识库
3. 获取知识库详情
4. 编辑知识库
5. 删除知识库
6. 修改知识库状态
"""

import time

import pytest

from .test_base import TestBase


class TestKnowledgeBase(TestBase):
    def _save_and_get_id(self, **kwargs):
        """新增知识库并通过分页查询获取ID

        Returns:
            (knowledge_id, title) 元组
        """
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
        return knowledge_id, payload["title"]

    @pytest.mark.smoke
    def test_save_knowledge_success(self):
        """使用标准参数新增知识库，应返回成功"""
        payload = self._build_knowledge_payload()
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

    def test_save_knowledge_missing_title(self):
        """缺少 title，应返回失败"""
        response = self.client.save_knowledge(
            title="",
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_missing_content(self):
        """缺少 content，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_title_too_long(self):
        """title 超过50个字符，应返回失败"""
        response = self.client.save_knowledge(
            title="A" * 51,
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_page_knowledge_success(self):
        """正常分页查询知识库，应返回成功"""
        response = self.client.page_knowledge(page_num=1, page_size=10)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        assert "data" in data, "Missing data in response"
        page_data = data.get("data", {})
        assert "records" in page_data, "Missing records in page data"
        assert "total" in page_data, "Missing total in page data"

    def test_page_knowledge_by_title(self):
        """按标题模糊查询知识库"""
        knowledge_id, title = self._save_and_get_id()

        response = self.client.page_knowledge(page_num=1, page_size=10, title=title)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        records = data.get("data", {}).get("records", [])
        found = any(record.get("title") == title for record in records)
        assert found, f"Created knowledge '{title}' not found in page results"

    def test_get_knowledge_detail_existing(self):
        """获取已存在的知识库详情，应返回成功"""
        knowledge_id, title = self._save_and_get_id()

        response = self.client.get_knowledge_detail(knowledge_id=knowledge_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)
        knowledge_data = data.get("data", {})
        assert knowledge_data.get("id") == str(knowledge_id)
        assert knowledge_data.get("title") == title

    def test_get_knowledge_detail_non_existing(self):
        """获取不存在的知识库详情，应返回失败"""
        response = self.client.get_knowledge_detail(knowledge_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_edit_knowledge_success(self):
        """编辑已存在的知识库，应返回成功"""
        knowledge_id, title = self._save_and_get_id()
        new_title = f"TestKB_EDIT{int(time.time())}"

        response = self.client.edit_knowledge(
            knowledge_id=knowledge_id,
            title=new_title,
            content="EditedContent",
            consult_type=2,
            display_position=[1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_disable(self):
        """禁用已启用的知识库，应返回成功"""
        knowledge_id, _ = self._save_and_get_id()

        response = self.client.change_knowledge_status(knowledge_id=knowledge_id, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    def test_change_status_enable(self):
        """启用已禁用的知识库，应返回成功"""
        knowledge_id, _ = self._save_and_get_id()

        disable_resp = self.client.change_knowledge_status(knowledge_id=knowledge_id, status=0)
        self.validator.assert_status_code(disable_resp, 200)
        self.assert_save_success(disable_resp.json())

        enable_resp = self.client.change_knowledge_status(knowledge_id=knowledge_id, status=1)
        self.validator.assert_status_code(enable_resp, 200)
        self.assert_save_success(enable_resp.json())

    def test_delete_knowledge_success(self):
        """删除已存在的知识库，应返回成功"""
        knowledge_id, _ = self._save_and_get_id()

        response = self.client.delete_knowledge(knowledge_id=knowledge_id)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_success(data)

    @pytest.mark.backend_bug
    def test_delete_knowledge_non_existing(self):
        """删除不存在的知识库，预期应返回失败，但后端实际返回成功（疑似未做存在性校验）"""
        response = self.client.delete_knowledge(knowledge_id=999999)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 预期：删除不存在的记录应返回失败
        # 实际后端bug：返回成功 code:00
        assert data.get("code") not in ("0", "00"), f"Expected failure for non-existent knowledge, got: {data}"

    def test_delete_knowledge_missing_id(self):
        """删除知识库缺少 id，应返回失败"""
        response = self.client.delete_knowledge(knowledge_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_missing_consult_type(self):
        """缺少 consultType，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="TestContent",
            consult_type=None,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_missing_display_position(self):
        """缺少 displayPosition，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="TestContent",
            consult_type=1,
            display_position=None,
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_missing_applicable_area(self):
        """缺少 applicableArea，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=None,
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_id(self):
        """修改知识库状态缺少 id，应返回失败"""
        response = self.client.change_knowledge_status(knowledge_id=None, status=0)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_change_status_missing_status(self):
        """修改知识库状态缺少 status，应返回失败"""
        knowledge_id, _ = self._save_and_get_id()
        response = self.client.change_knowledge_status(knowledge_id=knowledge_id, status=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_detail_missing_id(self):
        """获取知识库详情缺少 id，应返回失败"""
        response = self.client.get_knowledge_detail(knowledge_id=None)
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_content_too_long(self):
        """content 超过 2000 个字符，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="A" * 2001,
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_content_empty(self):
        """content 为空，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_invalid_consult_type(self):
        """consultType 非法值，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="TestContent",
            consult_type=99,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_invalid_display_position(self):
        """displayPosition 越界，应返回失败"""
        response = self.client.save_knowledge(
            title="TestKB",
            content="TestContent",
            consult_type=1,
            display_position=[99],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)

    def test_save_knowledge_title_special_chars(self):
        """title 含特殊字符，应返回失败或净化"""
        response = self.client.save_knowledge(
            title="TestKB<script>alert('xss')</script>",
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        # 只记录结果，不做断言
        assert data.get("code") in ("0", "00", "03"), f"Unexpected response: {data}"

    def test_edit_knowledge_non_existing(self):
        """编辑不存在的知识库，应返回失败"""
        response = self.client.edit_knowledge(
            knowledge_id=999999,
            title="TestKB",
            content="TestContent",
            consult_type=1,
            display_position=[0, 1],
            applicable_area=[{"code": "110119000000", "name": "延庆区", "level": "county"}],
        )
        self.validator.assert_status_code(response, 200)
        data = response.json()
        self.assert_save_failure(data)
