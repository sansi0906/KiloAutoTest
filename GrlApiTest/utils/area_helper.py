"""
area_helper.py - 区域数据工具
================================
提供区域树数据的获取、缓存和查询功能。
区域数据为静态参考数据，缓存后供后续接口测试复用。
"""

import functools

from api_clients.jeecgboot_client import JeecgBootClient


@functools.lru_cache(maxsize=1)
def get_area_tree(client: JeecgBootClient) -> list:
    """获取并缓存区域树数据

    Args:
        client: 已登录的 JeecgBootClient 实例

    Returns:
        区域树列表，每个节点包含 areaCode, areaName, level, children 等字段
    """
    response = client.post("/common/area/treeAll")
    response.raise_for_status()
    data = response.json()
    if data.get("code") not in ("0", "00"):
        raise RuntimeError(f"获取区域树失败: {data}")
    return data.get("data", {}).get("areaTreeJson", [])


def find_area_by_name(tree: list, name: str) -> dict | None:
    """在区域树中按名称查找节点（递归搜索）

    Args:
        tree: 区域树列表
        name: 区域名称（精确匹配）

    Returns:
        匹配的区域节点字典，未找到返回 None
    """
    for node in tree:
        if node.get("areaName") == name:
            return node
        children = node.get("children", [])
        if children:
            found = find_area_by_name(children, name)
            if found:
                return found
    return None


def build_area_code_map(tree: list) -> dict:
    """将区域树扁平化为 {areaName: areaCode} 映射

    Args:
        tree: 区域树列表

    Returns:
        区域名称到区域编码的映射字典
    """
    result = {}

    def _flatten(nodes):
        for node in nodes:
            result[node.get("areaName")] = node.get("areaCode")
            children = node.get("children", [])
            if children:
                _flatten(children)

    _flatten(tree)
    return result
