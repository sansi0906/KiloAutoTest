"""
data_driver.py - 数据驱动测试工具
==================================
支持从 JSON 和 YAML 文件加载测试数据
用于参数化测试，实现测试数据与测试逻辑分离
"""

import os
import json
import yaml


def load_json(path):
    """从 JSON 文件加载测试数据

    Args:
        path: JSON 文件路径

    Returns:
        解析后的 Python 对象（字典或列表）
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path):
    """从 YAML 文件加载测试数据

    Args:
        path: YAML 文件路径

    Returns:
        解析后的 Python 对象（字典或列表）
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_test_data(data_file):
    """根据文件扩展名自动选择加载方式

    Args:
        data_file: 数据文件路径（支持 .json、.yaml、.yml）

    Returns:
        解析后的测试数据

    Raises:
        ValueError: 不支持的文件格式
    """
    ext = os.path.splitext(data_file)[1].lower()
    if ext == ".json":
        return load_json(data_file)
    elif ext in (".yaml", ".yml"):
        return load_yaml(data_file)
    else:
        raise ValueError(f"Unsupported data file format: {ext}")