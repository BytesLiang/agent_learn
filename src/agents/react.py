"""ReAct Agent 实现."""
import json
import re
from typing import Dict, List

from src.model_client import ModelClient
from src.tools.registry import ToolRegistry
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class ReActAgent:
    """ReAct (Reasoning + Acting) Agent.

    遵循 ReAct 框架，交替进行推理和行动来回答问题。
    """

    _THOUGHT_PATTERN = re.compile(r"Thought:\s*(.+?)(?=\nAction:|$)", re.DOTALL)
    _ACTION_PATTERN = re.compile(r"Action:\s*(.+?)(?=\nAction Input:|$)", re.DOTALL)
    _ACTION_INPUT_PATTERN = re.compile(
        r"Action Input:\s*(\{.+?\}|\".*?\"|.+?)(?=\n|$)", re.DOTALL
    )

    def __init__(
        self,
        model_client: ModelClient,
        tool_registry: ToolRegistry,
        max_cycles: int = 10,
    ) -> None:
        """初始化 ReAct Agent.

        Args:
            model_client: 模型客户端
            tool_registry: 工具注册器
            max_cycles: 最大循环次数，默认 10
        """
        self.model = model_client
        self.tools = tool_registry
        self.max_cycles = max_cycles
        logger.debug(format_log_message(f"🧠 ReActAgent 初始化，最大轮次: {max_cycles}"))

    def run(self, question: str) -> str:
        """运行 Agent 回答问题.

        Args:
            question: 用户问题

        Returns:
            最终答案

        Raises:
            Exception: 执行过程中出错
        """
        logger.info(format_log_message(f"🎯 开始处理问题: {question[:50]}..."))

        system_prompt = self._build_system_prompt()
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        cycle_count = 0
        response = ""

        while cycle_count < self.max_cycles:
            cycle_count += 1
            logger.info(format_log_message(f"🔄 第 {cycle_count} 轮推理"))

            response = self.model.think(messages)
            logger.info(format_log_message(f"💭 模型响应: {response[:100]}..."))

            parsed = self._parse_response(response)
            if not parsed:
                logger.warning(format_log_message("⚠️ 无法解析模型响应，尝试继续..."))
                messages.append({"role": "assistant", "content": response})
                continue

            thought = parsed.get("thought", "")
            action = parsed.get("action", "").strip()
            action_input = parsed.get("action_input", "")

            logger.info(format_log_message(f"🧠 Thought: {thought[:50]}..."))
            logger.info(format_log_message(f"🔧 Action: {action}"))

            if action.lower() == "final answer":
                answer = self._extract_final_answer(action_input)
                logger.info(format_log_message(f"✅ 完成，最终答案: {answer[:50]}..."))
                return answer

            messages.append({"role": "assistant", "content": response})

            observation = self._execute_tool(action, action_input)
            logger.info(format_log_message(f"👁️ Observation: {observation[:50]}..."))

            observation_msg = f"\nObservation: {observation}"
            messages.append({"role": "user", "content": observation_msg})

        logger.warning(format_log_message(f"⚠️ 达到最大轮次 {self.max_cycles}，返回最后响应"))
        return response

    def _build_system_prompt(self) -> str:
        """构建系统提示词.

        Returns:
            系统提示词
        """
        tool_descriptions = self._format_tool_descriptions()
        tool_names = ", ".join(self.tools.list_tools())

        return f"""你是一个智能助手，可以使用工具来回答问题。

你可以使用以下工具：
{tool_descriptions}

重要：请严格按照以下格式输出，每行一个标签：

Thought: 你对问题的思考和推理
Action: 要使用的工具名称（必须是以下之一：{tool_names}）或 "Final Answer"
Action Input: 工具的参数（JSON格式，例如 {{"query": "搜索内容"}}）或最终答案（JSON格式，例如 {{"answer": "你的答案"}}）

如果需要使用工具，必须先输出 Thought 和 Action，然后等待工具执行结果后，再输出下一个 Thought。

示例：
Thought: 我需要搜索 Python 创始人的信息
Action: web_search
Action Input: {{"query": "Python 创始人是谁"}}

Observation: （这是工具返回的结果）

Thought: 根据搜索结果，我找到了答案
Action: Final Answer
Action Input: {{"answer": "Python 的创始人是 Guido van Rossum"}}

现在开始回答问题。
你必须先输出 Thought: 标签。"""

    def _format_tool_descriptions(self) -> str:
        """格式化工具描述.

        Returns:
            工具描述字符串
        """
        descriptions = []
        for tool_name in self.tools.list_tools():
            tool = self.tools.get_tool(tool_name)
            desc = getattr(tool, "description", "无描述")
            descriptions.append(f"- {tool_name}: {desc}")
        return "\n".join(descriptions)

    def _parse_response(self, response: str) -> Dict[str, str]:
        """解析模型响应，提取 Thought、Action、Action Input.

        Args:
            response: 模型响应文本

        Returns:
            解析后的字典，包含 thought, action, action_input
        """
        result: Dict[str, str] = {}

        thought_match = self._THOUGHT_PATTERN.search(response)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        action_match = self._ACTION_PATTERN.search(response)
        if action_match:
            result["action"] = action_match.group(1).strip()

        action_input_match = self._ACTION_INPUT_PATTERN.search(response)
        if action_input_match:
            result["action_input"] = action_input_match.group(1).strip()

        return result

    def _execute_tool(self, tool_name: str, action_input: str) -> str:
        """执行工具.

        Args:
            tool_name: 工具名称
            action_input: 工具参数（JSON 字符串）

        Returns:
            工具执行结果

        Raises:
            ValueError: 工具名称无效或参数解析失败
            Exception: 工具执行失败
        """
        try:
            params = json.loads(action_input)
        except json.JSONDecodeError as e:
            logger.warning(
                format_log_message(f"⚠️ 解析 Action Input 失败: {e}")
            )
            params = {"query": action_input}

        try:
            result = self.tools.execute(tool_name, **params)
            return str(result)
        except ValueError as e:
            logger.error(format_log_message(f"❌ 工具执行失败: {e}"))
            return f"工具执行失败: {e}"
        except Exception as e:
            logger.exception(format_log_message(f"❌ 工具执行异常: {e}"))
            return f"工具执行失败: {e}"

    def _extract_final_answer(self, action_input: str) -> str:
        """提取最终答案.

        Args:
            action_input: 包含答案的字符串

        Returns:
            答案文本
        """
        try:
            data = json.loads(action_input)
            return data.get("answer", action_input)
        except json.JSONDecodeError:
            return action_input.strip('"')
