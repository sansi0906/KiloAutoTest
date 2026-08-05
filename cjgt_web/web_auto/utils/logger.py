# -*- coding: utf-8 -*-
"""统一日志封装"""
import logging
import os
import sys
from datetime import datetime

from config.env_config import REPORT_DIR


def setup_logger(name: str = "web_auto", level: int = logging.INFO) -> logging.Logger:
    """创建/获取 logger，控制台 + 文件双输出"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # 文件
    os.makedirs(REPORT_DIR, exist_ok=True)
    log_file = os.path.join(REPORT_DIR, f"run_{datetime.now():%Y%m%d}.log")
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


logger = setup_logger()
