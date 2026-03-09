"""回答阶段节点 - 生成回答."""

from typing import Any

from src.agents.langgraph_qa.states import IntentType
from src.model_client import ModelClient
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


def answer_node(state: dict[str, Any], model_client: ModelClient) -> dict[str, Any]:
    """回答阶段节点：生成最终回答.

    Args:
        state: 当前状态
        model_client: 模型客户端

    Returns:
        更新后的状态字典
    """
    question = state.get("question", "")
    intent_analysis = state.get("intent_analysis")
    search_results = state.get("search_results", [])

    logger.info(format_log_message("📝 回答阶段: 生成最终回答"))

    if not search_results:
        final_answer = _generate_answer_without_search(question, model_client)
    else:
        final_answer = _generate_answer_with_search(
            question, intent_analysis, search_results, model_client
        )

    logger.info(format_log_message(f"✅ 回答生成完成: {final_answer[:50]}..."))

    return {"final_answer": final_answer}


def _generate_answer_with_search(
    question: str,
    intent_analysis: Any,
    search_results: list[Any],
    model_client: ModelClient,
) -> str:
    """基于搜索结果生成回答.

    Args:
        question: 用户问题
        intent_analysis: 意图分析结果
        search_results: 搜索结果列表
        model_client: 模型客户端

    Returns:
        生成的回答
    """
    context_parts = []
    for i, result in enumerate(search_results, 1):
        title = getattr(result, "title", result.get("title", "") if isinstance(result, dict) else "")
        source = getattr(result, "source", result.get("source", "") if isinstance(result, dict) else "")
        content = getattr(result, "content", result.get("content", "") if isinstance(result, dict) else "")
        context_parts.append(f"[{i}] {title}\n来源: {source}\n内容: {content}")

    context = "\n\n".join(context_parts)

    intent_type = None
    if intent_analysis:
        intent_type = getattr(intent_analysis, "intent_type", None)
        if intent_type is None and isinstance(intent_analysis, dict):
            from src.agents.langgraph_qa.states import IntentType
            intent_type_str = intent_analysis.get("intent_type", "fact")
            intent_type = IntentType(intent_type_str)

    intent_guidance = _get_intent_guidance(intent_type) if intent_type else "- 回答问题并提供相关信息"

    prompt = f"""请基于以下搜索结果回答用户问题。

用户问题：{question}

搜索结果：
{context}

回答要求：
{intent_guidance}

请生成一个自然、准确、简洁的回答，并在回答中引用关键信息来源（使用 [1], [2] 等标注）。"""

    messages = [{"role": "user", "content": prompt}]
    return model_client.think(messages)


def _generate_answer_without_search(question: str, model_client: ModelClient) -> str:
    """无搜索结果时直接生成回答.

    Args:
        question: 用户问题
        model_client: 模型客户端

    Returns:
        生成的回答
    """
    prompt = f"""请回答以下问题。如果问题涉及具体事实，请说明这是基于一般知识的回答。

用户问题：{question}

请生成一个简洁、准确的回答。"""

    messages = [{"role": "user", "content": prompt}]
    return model_client.think(messages)


def _get_intent_guidance(intent_type: IntentType | None) -> str:
    """根据意图类型获取回答指导.

    Args:
        intent_type: 意图类型

    Returns:
        回答指导文本
    """
    if intent_type == IntentType.FACT:
        return """- 直接回答问题中的事实点
- 提供准确的数据和信息
- 引用可靠的信息来源"""

    elif intent_type == IntentType.EXPLANATION:
        return """- 解释原因或原理
- 提供清晰的逻辑链条
- 使用通俗易懂的语言"""

    elif intent_type == IntentType.RECOMMENDATION:
        return """- 提供具体的建议或推荐
- 说明推荐理由
- 如有多个选项，进行对比分析"""

    return "- 回答问题并提供相关信息"
