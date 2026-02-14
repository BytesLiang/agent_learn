"""测试工具模块."""
from src.tools.search import WebSearchTool
from src.tools.registry import ToolRegistry


def test_web_search():
    """测试网页搜索工具."""
    print("=== 测试 WebSearchTool ===")
    tool = WebSearchTool()

    # 测试有直接答案的搜索
    print("\n--- 测试直接答案 ---")
    result = tool.execute("What is the capital of France?")
    print(result)

    # 测试需要摘要的搜索
    print("\n--- 测试网页摘要 ---")
    result = tool.execute("Python web framework comparison")
    print(result)


def test_tool_registry():
    """测试工具注册器."""
    print("\n=== 测试 ToolRegistry ===")
    registry = ToolRegistry()

    # 注册工具
    search_tool = WebSearchTool()
    registry.register(search_tool)

    # 列出工具
    print(f"已注册工具: {registry.list_tools()}")

    # 执行工具
    result = registry.execute("web_search", query="What is AI?")
    print(f"执行结果: {result[:200]}...")


if __name__ == "__main__":
    test_web_search()
    test_tool_registry()
