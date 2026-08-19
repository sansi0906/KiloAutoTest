"""
base_client.py - 基础 HTTP 客户端
=================================
封装 requests.Session，提供统一的请求方法
支持自动携带 Token 头、超时设置、会话复用
提供通用 CRUD 辅助方法，减少子类重复代码
"""

import requests


class BaseClient:
    def __init__(self, base_url="", timeout=30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        self._request_history = []
        self._max_history = 100

    def set_token(self, token):
        """设置请求头中的 token，用于后续需要认证的接口"""
        self.token = token
        if token:
            self.session.headers.update({"token": token})

    def clear_token(self):
        """清除请求头中的 token"""
        self.token = None
        self.session.headers.pop("token", None)

    def request(self, method, path, **kwargs):
        """发起 HTTP 请求，自动拼接基础 URL 和超时设置"""
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, url, **kwargs)
        try:
            resp_json = response.json() if response.content else None
        except ValueError:
            resp_json = {"_raw": response.text[:500]} if response.text else None

        self._request_history.append({
            "method": method,
            "url": url,
            "body": kwargs.get("json") if kwargs.get("json") is not None else (kwargs.get("data") if kwargs.get("data") else None),
            "response": {
                "status": response.status_code,
                "json": resp_json,
            } if response.content else {"status": response.status_code, "json": None},
        })
        if len(self._request_history) > self._max_history:
            self._request_history.pop(0)
        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        if kwargs.get("files"):
            self.session.headers.pop("Content-Type", None)
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def _build_payload(self, **fields):
        """构建 JSON 请求体，自动过滤 None 值"""
        return {k: v for k, v in fields.items() if v is not None}

    def _save(self, path, **fields):
        """通用保存方法：POST 到 /xxx/save"""
        return self.post(path, json=self._build_payload(**fields))

    def _page(self, path, page_num=1, page_size=10, **filters):
        """通用分页查询方法：POST 到 /xxx/paging 或 /xxx/page"""
        payload = {"pageNum": page_num, "pageSize": page_size}
        payload.update(self._build_payload(**filters))
        return self.post(path, json=payload)

    def _detail(self, path, id_value, id_field="id"):
        """通用详情查询方法：POST 到 /xxx/detail"""
        return self.post(path, json={id_field: id_value})

    def _edit(self, path, id_value, id_field="id", **fields):
        """通用编辑方法：POST 到 /xxx/edit"""
        payload = self._build_payload(**fields)
        payload[id_field] = id_value
        return self.post(path, json=payload)

    def _delete(self, path, id_value, id_field="id"):
        """通用删除方法：POST 到 /xxx/delete"""
        return self.post(path, json={id_field: id_value})

    def _change_status(self, path, id_value, status, id_field="id", status_field="status"):
        """通用状态切换方法：POST 到 /xxx/changeStatus"""
        return self.post(path, json={id_field: id_value, status_field: status})
