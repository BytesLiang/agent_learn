"""LangGraph 问答对话助手核心实现."""

from typing import Any

from langgraph.graph import END, StateGraph

from src.agents.langgraph_qa.nodes.answer import answer_node
from src.agents.langgraph_qa.nodes.search import search_node
from src.agents.langgraph_qa.nodes.understand import understand_node
from src.agents.langgraph_qa.states import QAState
from src.model_client import ModelClient
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class LangGraphQAAgent:
    """基于 LangGraph 的问答对话助手.

    遵循三阶段流程：理解 → 搜索 → 回答
    """

    def __init__(self, model_client: ModelClient) -> None:
        """初始化问答助手.

        Args:
            model_client: 模型客户端
        """
        self.model_client = model_client
        self.graph = self._build_graph()
        logger.info(format_log_message("🚀 LangGraphQAAgent 初始化成功"))

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图.

        Returns:
            配置好的状态图
        """
        builder = StateGraph(QAState)

        builder.add_node("understand", self._understand_wrapper)
        builder.add_node("search", self._search_wrapper)
        builder.add_node("answer", self._answer_wrapper)

        builder.set_entry_point("understand")

        builder.add_edge("understand", "search")
        builder.add_edge("search", "answer")
        builder.add_edge("answer", END)

        return builder.compile()

    def _understand_wrapper(self, state: QAState) -> dict[str, Any]:
        """理解阶段节点包装器.

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        return understand_node(state, self.model_client)

    def _search_wrapper(self, state: QAState) -> dict[str, Any]:
        """搜索阶段节点包装器.

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        return search_node(state)

    def _answer_wrapper(self, state: QAState) -> dict[str, Any]:
        """回答阶段节点包装器.

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        return answer_node(state, self.model_client)

    def run(self, question: str) -> str:
        """运行问答助手处理问题.

        Args:
            question: 用户问题

        Returns:
            最终回答
        """
        logger.info(format_log_message(f"🎯 开始处理问题: {question[:50]}..."))

        initial_state: QAState = {
            "question": question,
            "messages": [],
            "intent_analysis": None,
            "search_results": [],
            "final_answer": "",
        }

        result = self.graph.invoke(initial_state)

        final_answer = result.get("final_answer", "") if result else ""
        logger.info(format_log_message("✅ 处理完成"))

        return final_answer

    def run_with_details(self, question: str) -> dict[str, Any]:
        """运行问答助手并返回详细结果.

        Args:
            question: 用户问题

        Returns:
            包含完整状态的字典
        """
        logger.info(
            format_log_message(f"🎯 开始处理问题（详细模式）: {question[:50]}...")
        )

        initial_state: QAState = {
            "question": question,
            "messages": [],
            "intent_analysis": None,
            "search_results": [],
            "final_answer": "",
        }

        result = self.graph.invoke(initial_state)

        if not result:
            return dict(initial_state)

        result_dict = dict(result)

        if result_dict.get("intent_analysis"):
            intent = result_dict["intent_analysis"]
            if hasattr(intent, "to_dict"):
                result_dict["intent_analysis"] = intent.to_dict()

        if result_dict.get("search_results"):
            result_dict["search_results"] = [
                sr.to_dict() if hasattr(sr, "to_dict") else sr
                for sr in result_dict["search_results"]
            ]

        logger.info(format_log_message("✅ 处理完成（详细模式）"))

        return result_dict
