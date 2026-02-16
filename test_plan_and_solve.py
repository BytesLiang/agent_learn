"""测试 Plan-and-Solve Agent."""
from src.agents.plan_and_solve import PlanAndSolveAgent
from src.model_client import ModelClient
from src.tools.registry import ToolRegistry
from src.tools.search import WebSearchTool


def test_plan_and_solve_agent():
    """测试 Plan-and-Solve Agent."""
    print("=== 初始化组件 ===")

    model_client = ModelClient()
    registry = ToolRegistry()
    registry.register(WebSearchTool())

    agent = PlanAndSolveAgent(model_client, registry, max_cycles=5)

    print("\n=== 测试 Plan-and-Solve Agent ===")

    questions = [
        "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？",
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
    test_plan_and_solve_agent()
