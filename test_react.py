"""测试 ReAct Agent."""
from src.agents.react import ReActAgent
from src.model_client import ModelClient
from src.tools.registry import ToolRegistry
from src.tools.search import WebSearchTool


def test_react_agent():
    """测试 ReAct Agent."""
    print("=== 初始化组件 ===")

    model_client = ModelClient()
    registry = ToolRegistry()
    registry.register(WebSearchTool())

    agent = ReActAgent(model_client, registry, max_cycles=5)

    print("\n=== 测试 ReAct Agent ===")

    questions = [
        "华为最新旗舰手机的价格",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 50)
        try:
            answer = agent.run(question)
            print(f"\n最终答案: {answer}")
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    test_react_agent()
