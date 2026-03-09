"""理解阶段节点 - 意图分析."""

import json
import re
from typing import Any

from src.agents.langgraph_qa.states import IntentAnalysis, IntentType
from src.model_client import ModelClient
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


def understand_node(state: dict[str, Any], model_client: ModelClient) -> dict[str, Any]:
    """理解阶段节点：分析用户意图.

    Args:
        state: 当前状态
        model_client: 模型客户端

    Returns:
        更新后的状态字典
    """
    question = state.get("question", "")
    logger.info(format_log_message(f"🎯 理解阶段: 分析问题 '{question[:50]}...'"))

    prompt = f"""请分析以下用户问题的意图，并输出结构化的分析结果。

用户问题：{question}

请按以下 JSON 格式输出分析结果：
{{
    "intent_type": "fact|explanation|recommendation",
    "entities": ["关键实体1", "关键实体2"],
    "context": "问题的上下文描述",
    "confidence": 0.0-1.0
}}

意图类型说明：
- fact: 事实型查询，询问具体事实或信息
- explanation: 解释型查询，要求解释原因或原理
- recommendation: 建议型查询，寻求建议或推荐

请只输出 JSON，不要输出其他内容。"""

    messages = [{"role": "user", "content": prompt}]
    response = model_client.think(messages)

    intent_analysis = _parse_intent_response(response, question)

    logger.info(
        format_log_message(
            f"✅ 意图分析完成: 类型={intent_analysis.intent_type.value}, "
            f"实体={intent_analysis.entities}"
        )
    )

    return {"intent_analysis": intent_analysis}


def _parse_intent_response(response: str, question: str) -> IntentAnalysis:
    """解析模型响应，提取意图分析结果.

    Args:
        response: 模型响应
        question: 原始问题

    Returns:
        意图分析结果
    """
    json_match = re.search(r"\{[\s\S]*\}", response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            intent_type_str = data.get("intent_type", "fact").lower()

            intent_type = IntentType.FACT
            if intent_type_str == "explanation":
                intent_type = IntentType.EXPLANATION
            elif intent_type_str == "recommendation":
                intent_type = IntentType.RECOMMENDATION

            return IntentAnalysis(
                intent_type=intent_type,
                entities=data.get("entities", []),
                context=data.get("context", ""),
                confidence=float(data.get("confidence", 1.0)),
            )
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(format_log_message(f"⚠️ JSON 解析失败: {e}"))

    return _infer_intent_from_question(question)


def _infer_intent_from_question(question: str) -> IntentAnalysis:
    """从问题文本推断意图.

    Args:
        question: 用户问题

    Returns:
        意图分析结果
    """
    question_lower = question.lower()

    explanation_keywords = ["为什么", "怎么", "如何", "原因", "原理", "why", "how"]
    recommendation_keywords = [
        "应该",
        "推荐",
        "建议",
        "哪个",
        "选择",
        "should",
        "recommend",
    ]

    intent_type = IntentType.FACT
    for keyword in explanation_keywords:
        if keyword in question_lower:
            intent_type = IntentType.EXPLANATION
            break

    if intent_type == IntentType.FACT:
        for keyword in recommendation_keywords:
            if keyword in question_lower:
                intent_type = IntentType.RECOMMENDATION
                break

    entities = _extract_entities(question)

    return IntentAnalysis(
        intent_type=intent_type,
        entities=entities,
        context=f"从问题推断的意图: {question}",
        confidence=0.7,
    )


def _extract_entities(question: str) -> list[str]:
    """从问题中提取关键实体.

    Args:
        question: 用户问题

    Returns:
        关键实体列表
    """
    stop_words = {
        "的",
        "是",
        "在",
        "有",
        "和",
        "了",
        "我",
        "你",
        "他",
        "她",
        "它",
        "这",
        "那",
        "什么",
        "怎么",
        "如何",
        "为什么",
        "哪个",
        "哪些",
        "应该",
        "可以",
        "能",
        "会",
        "吗",
        "呢",
        "啊",
        "吧",
    }

    words = re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", question)
    entities = [w for w in words if w not in stop_words and len(w) > 1]

    return entities[:5]
