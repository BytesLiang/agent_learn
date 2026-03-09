"""搜索阶段节点 - 使用 Tavily API 搜索."""

from typing import Any

from src.agents.langgraph_qa.states import IntentType, QAState, SearchResult
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)

MAX_RESULTS = 5
TAVILY_TIMEOUT = 30

_tavily_client = None


def _get_tavily_client() -> Any | None:
    """获取 Tavily 客户端实例（懒加载）.

    Returns:
        Tavily 客户端实例，如果不可用则返回 None
    """
    global _tavily_client

    if _tavily_client is not None:
        return _tavily_client

    try:
        import os

        from tavily import TavilyClient

        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            logger.error(format_log_message("❌ TAVILY_API_KEY 未配置"))
            return ValueError("TAVILY_API_KEY 未配置")

        _tavily_client = TavilyClient(api_key=api_key)
        logger.info(format_log_message("✅ Tavily 客户端初始化成功"))
        return _tavily_client

    except ImportError:
        logger.error(format_log_message("❌ tavily-python 未安装"))
        return None
    except Exception as e:
        logger.error(
            format_log_message(f"❌ Tavily 客户端初始化失败: {e}")
        )
        return None


def search_node(state: QAState) -> dict[str, Any]:
    """搜索阶段节点：使用 Tavily API 搜索相关信息.

    Args:
        state: 当前状态

    Returns:
        更新后的状态字典
    """
    intent_analysis = state.get("intent_analysis")
    question = state.get("question", "")

    logger.info(format_log_message("🔍 搜索阶段: 基于意图搜索相关信息"))

    if not intent_analysis:
        logger.warning(format_log_message("⚠️ 无意图分析结果，返回空搜索结果"))
        return {"search_results": []}

    search_query = _build_search_query(intent_analysis.entities, question)

    search_results = _perform_tavily_search(search_query)

    if not search_results:
        logger.error(format_log_message("❌ Tavily 无结果"))
        return {"search_results": []}

    search_results = _rank_by_relevance(search_results, intent_analysis)

    search_results = search_results[:MAX_RESULTS]

    logger.info(
        format_log_message(f"✅ 搜索完成: 找到 {len(search_results)} 条相关结果")
    )

    return {"search_results": search_results}


def _build_search_query(entities: list[str], question: str) -> str:
    """构建搜索查询.

    Args:
        entities: 关键实体列表
        question: 原始问题

    Returns:
        优化后的搜索查询
    """
    if entities:
        entity_str = " ".join(entities[:3])
        return f"{entity_str} {question}"
    return question


def _perform_tavily_search(query: str) -> list[SearchResult]:
    """使用 Tavily API 执行搜索.

    Args:
        query: 搜索查询

    Returns:
        搜索结果列表
    """
    client = _get_tavily_client()
    if not client:
        return []

    try:
        logger.info(format_log_message(f"🌐 Tavily API 搜索: {query[:50]}..."))

        response = client.search(
            query=query,
            max_results=MAX_RESULTS,
            include_answer=True,
            include_raw_content=False,
        )

        results: list[SearchResult] = []

        if "answer" in response and response["answer"]:
            results.append(
                SearchResult(
                    title="AI 生成答案",
                    content=response["answer"],
                    source="Tavily AI",
                    relevance_score=1.0,
                )
            )

        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    source=item.get("url", ""),
                    relevance_score=item.get("score", 0.8),
                )
            )

        logger.info(format_log_message(f"✅ Tavily API 返回 {len(results)} 条结果"))
        return results

    except TimeoutError as e:
        logger.error(format_log_message(f"❌ Tavily API 超时: {e}"))
        return []
    except Exception as e:
        logger.error(format_log_message(f"❌ Tavily API 调用失败: {e}"))
        return []


def _rank_by_relevance(
    results: list[SearchResult], intent_analysis: Any
) -> list[SearchResult]:
    """按相关性排序搜索结果.

    Args:
        results: 搜索结果列表
        intent_analysis: 意图分析结果

    Returns:
        排序后的搜索结果列表
    """
    for result in results:
        score = result.relevance_score

        for entity in intent_analysis.entities:
            if entity.lower() in result.title.lower():
                score += 0.1
            if entity.lower() in result.content.lower():
                score += 0.05

        if intent_analysis.intent_type == IntentType.EXPLANATION:
            if "原因" in result.title or "为什么" in result.content:
                score += 0.15
        elif intent_analysis.intent_type == IntentType.RECOMMENDATION:
            if "对比" in result.title or "推荐" in result.content:
                score += 0.15

        result.relevance_score = min(score, 1.0)

    return sorted(results, key=lambda x: x.relevance_score, reverse=True)
