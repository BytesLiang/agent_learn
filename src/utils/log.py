"""共享日志工具."""
import logging
from datetime import datetime


def format_log_message(msg: str) -> str:
    """格式化日志消息，添加时间戳.

    Args:
        msg: 原始日志消息

    Returns:
        格式化后的日志消息
    """
    return f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器.

    Args:
        name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
