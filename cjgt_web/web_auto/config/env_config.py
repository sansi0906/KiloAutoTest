# -*- coding: utf-8 -*-
"""环境配置读取 —— 从 .env 加载，供全局使用"""
import os
from dotenv import load_dotenv

# 加载 .env（与本文件同目录）
# 注意：override=True 用于覆盖 Windows 系统级环境变量（如 USERNAME 会与 .env 冲突）
_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_ENV_PATH, override=True)


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _get_bool(key: str, default: bool = False) -> bool:
    return _get(key, str(default)).lower() in ("true", "1", "yes", "on")


def _get_int(key: str, default: int = 0) -> int:
    try:
        return int(_get(key, str(default)))
    except ValueError:
        return default


# ── 被测系统 ──
BASE_URL: str = _get("BASE_URL", "")
USERNAME: str = _get("USERNAME", "")
PASSWORD: str = _get("PASSWORD", "")

# ── 浏览器 ──
HEADLESS: bool = _get_bool("HEADLESS", False)
BROWSER: str = _get("BROWSER", "chromium")
VIEWPORT_WIDTH: int = _get_int("VIEWPORT_WIDTH", 1440)
VIEWPORT_HEIGHT: int = _get_int("VIEWPORT_HEIGHT", 900)
PROXY: str = _get("PROXY", "")

# ── 超时 ──
TIMEOUT: int = _get_int("TIMEOUT", 30000)

# ── 并行 ──
PARALLEL_WORKERS: int = _get_int("PARALLEL_WORKERS", 1)

# ── 路径 ──
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR: str = os.path.join(PROJECT_ROOT, "reports")
SCREENSHOT_DIR: str = os.path.join(REPORT_DIR, "screenshots")
