"""LangGraph 问答助手状态定义."""

from enum import Enum
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class IntentType(str, Enum):
    """意图类型枚举."""

    FACT = "fact"
    EXPLANATION = "explanation"
    RECOMMENDATION = "recommendation"


class IntentAnalysis:
    """意图分析结果."""

    def __init__(
        self,
        intent_type: IntentType,
        entities: list[str],
        context: str,
        confidence: float = 1.0,
    ) -> None:
        """初始化意图分析结果.

        Args:
            intent_type: 意图类型
            entities: 关键实体列表
            context: 上下文信息
            confidence: 置信度，默认 1.0
        """
        self.intent_type = intent_type
        self.entities = entities
        self.context = context
        self.confidence = confidence

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式."""
        return {
            "intent_type": self.intent_type.value,
            "entities": self.entities,
            "context": self.context,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntentAnalysis":
        """从字典创建实例."""
        return cls(
            intent_type=IntentType(data["intent_type"]),
            entities=data["entities"],
            context=data["context"],
            confidence=data.get("confidence", 1.0),
        )


class SearchResult:
    """搜索结果项."""

    def __init__(
        self,
        title: str,
        content: str,
        source: str,
        relevance_score: float = 1.0,
    ) -> None:
        """初始化搜索结果.

        Args:
            title: 结果标题
            content: 结果内容
            source: 信息来源
            relevance_score: 相关性分数，默认 1.0
        """
        self.title = title
        self.content = content
        self.source = source
        self.relevance_score = relevance_score

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式."""
        return {
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchResult":
        """从字典创建实例."""
        return cls(
            title=data["title"],
            content=data["content"],
            source=data["source"],
            relevance_score=data.get("relevance_score", 1.0),
        )


def merge_state(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    """合并状态的 reducer 函数.

    Args:
        left: 原状态
        right: 新状态（增量）

    Returns:
        合并后的状态
    """
    if left is None:
        left = {}
    if right is None:
        right = {}
    result = dict(left)
    result.update(right)
    return result


class QAState(TypedDict):
    """问答助手状态."""

    question: str
    messages: Annotated[list[BaseMessage], add_messages]
    intent_analysis: Any
    search_results: list[Any]
    final_answer: str
