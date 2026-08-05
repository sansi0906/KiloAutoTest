# -*- coding: utf-8 -*-
"""文件与截图路径处理"""
import os
import shutil
from datetime import datetime

from config.env_config import SCREENSHOT_DIR


def ensure_dir(path: str) -> str:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
    return path


def screenshot_path(name: str, sub_dir: str = "") -> str:
    """生成截图文件路径"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(SCREENSHOT_DIR, sub_dir) if sub_dir else SCREENSHOT_DIR
    ensure_dir(folder)
    return os.path.join(folder, f"{name}_{ts}.png")


def clean_dir(path: str) -> None:
    """清空目录（保留目录本身）"""
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
