"""工具执行器模块."""
from typing import Any

from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """工具注册器，支持动态发现和调度工具."""

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}
        logger.info(format_log_message("📋 ToolRegistry 初始化成功"))

    def register(self, tool: Any) -> None:
        """注册工具.

        Args:
            tool: 工具实例，必须有 name 属性
        """
        if not hasattr(tool, "name"):
            raise ValueError("工具必须有 name 属性")

        tool_name = tool.name
        self._tools[tool_name] = tool
        logger.info(format_log_message(f"✅ 注册工具: {tool_name}"))

    def execute(self, tool_name: str, **kwargs: Any) -> Any:
        """执行工具.

        Args:
            tool_name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果

        Raises:
            ValueError: 工具不存在
        """
        if tool_name not in self._tools:
            raise ValueError(f"工具不存在: {tool_name}")

        tool = self._tools[tool_name]
        logger.info(format_log_message(f"▶️ 执行工具: {tool_name}"))

        result = tool.execute(**kwargs)
        logger.info(format_log_message(f"✅ 工具执行完成: {tool_name}"))
        return result

    def list_tools(self) -> list[str]:
        """列出所有已注册的工具.

        Returns:
            工具名称列表
        """
        return list(self._tools.keys())

    def get_tool(self, tool_name: str) -> Any:
        """获取工具实例.

        Args:
            tool_name: 工具名称

        Returns:
            工具实例

        Raises:
            ValueError: 工具不存在
        """
        if tool_name not in self._tools:
            raise ValueError(f"工具不存在: {tool_name}")
        return self._tools[tool_name]
