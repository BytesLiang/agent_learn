"""测试 Reflection Agent."""
from src.agents.reflection import ReflectionAgent
from src.model_client import ModelClient


def test_reflection_agent():
    """测试 Reflection Agent."""
    print("=== 初始化组件 ===")

    model_client = ModelClient()
    agent = ReflectionAgent(model_client, max_iterations=3)

    print("\n=== 测试 Reflection Agent ===")

    questions = [
        "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 50)
        try:
            answer = agent.run(question)
            print(f"\n最终回答:\n{answer}")
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    test_reflection_agent()
