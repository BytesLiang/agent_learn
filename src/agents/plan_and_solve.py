"""Plan-and-Solve Agent 实现."""
import json
import re
from typing import Dict, List

from src.model_client import ModelClient
from src.tools.registry import ToolRegistry
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class PlanAndSolveAgent:
    """Plan-and-Solve Agent.

    先规划再执行的 Agent，分两阶段：
    1. 规划阶段：生成步骤列表
    2. 执行阶段：逐步执行每个步骤
    """

    _PLAN_PATTERN = re.compile(r"(?:^|\n)\s*(\d+)[\.、]\s*(.+?)(?=\n\d|\n*$)", re.DOTALL)
    _STEP_PATTERN = re.compile(r"Thought:\s*(.+?)\nAction:\s*(.+?)(?:\nAction Input:\s*(\{.+?\}|.+?))?", re.DOTALL)

    def __init__(
        self,
        model_client: ModelClient,
        tool_registry: ToolRegistry,
        max_cycles: int = 10,
    ) -> None:
        """初始化 PlanAndSolveAgent.

        Args:
            model_client: 模型客户端
            tool_registry: 工具注册器
            max_cycles: 最大循环次数，默认 10
        """
        self.model = model_client
        self.tools = tool_registry
        self.max_cycles = max_cycles
        logger.debug(format_log_message(f"🧠 PlanAndSolveAgent 初始化，最大轮次: {max_cycles}"))

    def run(self, question: str) -> str:
        """运行 Agent 回答问题.

        Args:
            question: 用户问题

        Returns:
            最终答案
        """
        logger.info(format_log_message(f"🎯 开始处理问题: {question[:50]}..."))

        system_prompt = self._build_planning_prompt()
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]

        plan = self._create_plan(messages)
        if not plan:
            logger.warning(format_log_message("⚠️ 无法生成计划，尝试直接回答"))
            return self._answer_directly(question)

        logger.info(format_log_message(f"📋 计划: {len(plan)} 个步骤"))
        for i, step in enumerate(plan, 1):
            logger.info(format_log_message(f"  {i}. {step}"))

        answer = self._execute_plan(question, plan)
        return answer

    def _build_planning_prompt(self) -> str:
        """构建规划阶段提示词."""
        return """你是一个智能助手，善于将复杂问题分解为步骤来解决。

请首先制定一个计划来解决这个问题。计划应该是一个步骤列表。

重要：请严格按照以下格式输出：

Plan:
1. 第一个步骤
2. 第二个步骤
3. 第三个步骤
...

每个步骤应该清晰、具体，并且按顺序执行后能解决问题。

现在开始制定计划："""

    def _build_execution_prompt(self, question: str, plan: List[str], current_step: int, context: str = "") -> str:
        """构建执行阶段提示词.

        Args:
            question: 原始问题
            plan: 计划步骤列表
            current_step: 当前步骤索引
            context: 上一步的执行结果
        """
        tool_names = ", ".join(self.tools.list_tools())

        steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
        context_text = f"\n\n上一步结果：{context}" if context else ""
        remaining_steps = len(plan) - current_step - 1

        return f"""原始问题：{question}

计划步骤（共 {len(plan)} 步）：
{steps_text}

你正在执行第 {current_step + 1} 步：{plan[current_step]}
还有 {remaining_steps} 步需要完成{context_text}

你可以使用以下工具：
{self._format_tool_descriptions()}

请按照以下格式输出：

Thought: 你对当前步骤的思考和计算
Action: 要使用的工具名称（{tool_names}）或 "Continue" 或 "Final Answer"
Action Input: 工具参数（JSON格式）或空（如果不需要参数）

重要规则：
- 如果当前步骤需要使用工具来获取信息，使用工具并输出 Action
- 如果当前步骤可以基于上下文直接得出结论，输出 Action: Continue（将思考过程记录到 context）
- 在执行最后一步（第 {len(plan)} 步）时，必须输出 Action: Final Answer
- 最终答案格式：{{"answer": "你的答案"}}

现在开始执行第 {current_step + 1} 步："""

    def _format_tool_descriptions(self) -> str:
        """格式化工具描述."""
        descriptions = []
        for tool_name in self.tools.list_tools():
            tool = self.tools.get_tool(tool_name)
            desc = getattr(tool, "description", "无描述")
            descriptions.append(f"- {tool_name}: {desc}")
        return "\n".join(descriptions)

    def _create_plan(self, messages: List[Dict[str, str]]) -> List[str]:
        """创建计划.

        Args:
            messages: 对话消息

        Returns:
            步骤列表
        """
        logger.info(format_log_message("📝 正在生成计划..."))

        response = self.model.think(messages)
        logger.info(format_log_message(f"💭 计划响应: {response[:100]}..."))

        plan = self._parse_plan(response)
        return plan

    def _parse_plan(self, response: str) -> List[str]:
        """解析计划响应.

        Args:
            response: 模型响应

        Returns:
            步骤列表
        """
        steps: List[str] = []

        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(r"(?:^|[\.、])\s*(\d+)[\.、]\s*(.+)", line)
            if match:
                step = match.group(2).strip()
                if step:
                    steps.append(step)
            elif line.startswith("-") or line.startswith("•"):
                step = line.lstrip("-•").strip()
                if step:
                    steps.append(step)

        if not steps and "Plan:" in response:
            plan_text = response.split("Plan:")[-1]
            for line in plan_text.split("\n"):
                line = line.strip()
                if line and not line.startswith("-"):
                    parts = re.split(r"\.|\d+[\.、]", line)
                    for part in parts:
                        part = part.strip()
                        if part and len(part) > 5:
                            steps.append(part)

        return steps

    def _execute_plan(self, question: str, plan: List[str]) -> str:
        """执行计划.

        Args:
            question: 原始问题
            plan: 计划步骤列表

        Returns:
            最终答案
        """
        context = ""
        cycle_count = 0

        for step_idx, step in enumerate(plan):
            if cycle_count >= self.max_cycles:
                logger.warning(format_log_message(f"⚠️ 达到最大轮次 {self.max_cycles}"))
                break

            cycle_count += 1
            logger.info(format_log_message(f"🔄 执行步骤 {step_idx + 1}/{len(plan)}: {step[:30]}..."))

            execution_prompt = self._build_execution_prompt(question, plan, step_idx, context)
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": execution_prompt},
            ]

            response = self.model.think(messages)
            logger.info(format_log_message(f"💭 执行响应: {response[:100]}..."))

            parsed = self._parse_execution_response(response)

            action = parsed.get("action", "").lower().strip()

            if action == "final answer":
                answer = self._extract_final_answer(parsed.get("action_input", ""))
                logger.info(format_log_message(f"✅ 完成，最终答案: {answer[:50]}..."))
                return answer

            tool_name = parsed.get("action", "").strip()

            if tool_name.lower() == "continue":
                thought = parsed.get("thought", "")
                context = f"步骤 {step_idx + 1} 思考: {thought}"
                logger.info(format_log_message("➡️ 继续下一步"))
            elif tool_name and tool_name.lower() != "final answer":
                action_input = parsed.get("action_input", "")
                observation = self._execute_tool(tool_name, action_input)
                logger.info(format_log_message(f"👁️ 步骤结果: {observation[:50]}..."))
                context = f"步骤 {step_idx + 1} 结果: {observation}"

        logger.warning(format_log_message("⚠️ 计划执行完成但未得到最终答案"))
        return context if context else "无法完成任务"

    def _parse_execution_response(self, response: str) -> Dict[str, str]:
        """解析执行响应.

        Args:
            response: 模型响应

        Returns:
            解析后的字典
        """
        result: Dict[str, str] = {}

        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|$)", response, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        action_match = re.search(r"Action:\s*(.+?)(?=\nAction Input:|$)", response, re.DOTALL)
        if action_match:
            result["action"] = action_match.group(1).strip()

        action_input_match = re.search(
            r"Action Input:\s*(\{.+?\}|\".*?\"|.+?)(?=\n|$)", response, re.DOTALL
        )
        if action_input_match:
            result["action_input"] = action_input_match.group(1).strip()

        return result

    def _execute_tool(self, tool_name: str, action_input: str) -> str:
        """执行工具.

        Args:
            tool_name: 工具名称
            action_input: 工具参数

        Returns:
            工具执行结果
        """
        try:
            params = json.loads(action_input)
        except json.JSONDecodeError:
            logger.warning(format_log_message(f"⚠️ 解析 Action Input 失败: {action_input}"))
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

    def _answer_directly(self, question: str) -> str:
        """直接回答问题（无法生成计划时）.

        Args:
            question: 用户问题

        Returns:
            答案
        """
        logger.info(format_log_message("🔄 尝试直接回答..."))

        prompt = f"""请直接回答以下问题：

{question}

如果需要使用工具，请按以下格式输出：
Thought: 你对问题的思考
Action: 工具名称
Action Input: {{"参数"}}

如果已经有答案，请输出：
Thought: 你对问题的思考
Action: Final Answer
Action Input: {{"answer": "你的答案"}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.model.think(messages)

        parsed = self._parse_execution_response(response)
        action = parsed.get("action", "").lower().strip()

        if action == "final answer":
            return self._extract_final_answer(parsed.get("action_input", ""))

        if action and action != "final answer":
            observation = self._execute_tool(action, parsed.get("action_input", ""))
            return f"{observation}"

        return response
