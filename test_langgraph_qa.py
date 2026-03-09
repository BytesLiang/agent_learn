"""测试 LangGraph 问答对话助手."""
from src.agents.langgraph_qa import LangGraphQAAgent
from src.model_client import ModelClient


def test_fact_query():
    """测试事实型查询."""
    print("=== 测试事实型查询 ===")

    model_client = ModelClient()
    agent = LangGraphQAAgent(model_client)

    question = "Python 的创始人是谁？"
    print(f"问题: {question}")

    result = agent.run_with_details(question)

    print(f"\n意图分析: {result.get('intent_analysis')}")
    print(f"搜索结果数: {len(result.get('search_results', []))}")
    print(f"\n最终回答:\n{result.get('final_answer')}")


def test_explanation_query():
    """测试解释型查询."""
    print("\n=== 测试解释型查询 ===")

    model_client = ModelClient()
    agent = LangGraphQAAgent(model_client)

    question = "为什么 Python 如此流行？"
    print(f"问题: {question}")

    result = agent.run_with_details(question)

    print(f"\n意图分析: {result.get('intent_analysis')}")
    print(f"搜索结果数: {len(result.get('search_results', []))}")
    print(f"\n最终回答:\n{result.get('final_answer')}")


def test_recommendation_query():
    """测试建议型查询."""
    print("\n=== 测试建议型查询 ===")

    model_client = ModelClient()
    agent = LangGraphQAAgent(model_client)

    question = "我应该学习哪个 Python 框架？"
    print(f"问题: {question}")

    result = agent.run_with_details(question)

    print(f"\n意图分析: {result.get('intent_analysis')}")
    print(f"搜索结果数: {len(result.get('search_results', []))}")
    print(f"\n最终回答:\n{result.get('final_answer')}")


def test_state_flow():
    """测试状态流转正确性."""
    print("\n=== 测试状态流转 ===")

    model_client = ModelClient()
    agent = LangGraphQAAgent(model_client)

    question = "Python 是什么？"
    print(f"问题: {question}")

    result = agent.run_with_details(question)

    assert "question" in result, "状态中缺少 question"
    assert result["question"] == question, "question 不匹配"

    assert result.get("intent_analysis") is not None, "缺少意图分析结果"
    intent = result["intent_analysis"]
    assert "intent_type" in intent, "意图分析缺少 intent_type"
    assert "entities" in intent, "意图分析缺少 entities"

    assert isinstance(result.get("search_results"), list), "search_results 应为列表"
    assert len(result["search_results"]) <= 5, "搜索结果超过 5 条"

    assert result.get("final_answer"), "缺少最终回答"

    print("✅ 状态流转验证通过")
    print(f"  - 问题: {result['question']}")
    print(f"  - 意图类型: {intent['intent_type']}")
    print(f"  - 关键实体: {intent['entities']}")
    print(f"  - 搜索结果数: {len(result['search_results'])}")
    print(f"  - 回答长度: {len(result['final_answer'])} 字符")


def test_simple_run():
    """测试简单运行模式."""
    print("\n=== 测试简单运行模式 ===")

    model_client = ModelClient()
    agent = LangGraphQAAgent(model_client)

    question = "Java 是什么？"
    print(f"问题: {question}")

    answer = agent.run(question)

    print(f"\n回答:\n{answer}")

    assert answer, "回答不应为空"
    print("✅ 简单运行模式测试通过")


if __name__ == "__main__":
    test_fact_query()
    test_explanation_query()
    test_recommendation_query()
    test_state_flow()
    test_simple_run()
