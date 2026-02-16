"""Reflection Agent 实现."""
from typing import List, Dict

from src.model_client import ModelClient
from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class ReflectionAgent:
    """Reflection Agent.

    通过迭代反思来改进回答质量的 Agent：
    生成 → 反思 → 改进 → 循环
    """

    def __init__(
        self,
        model_client: ModelClient,
        max_iterations: int = 3,
    ) -> None:
        """初始化 ReflectionAgent.

        Args:
            model_client: 模型客户端
            max_iterations: 最大迭代次数，默认 3
        """
        self.model = model_client
        self.max_iterations = max_iterations
        logger.info(format_log_message(f"🔄 ReflectionAgent 初始化，最大迭代: {max_iterations}"))

    def run(self, question: str) -> str:
        """运行 Agent 回答问题.

        Args:
            question: 用户问题

        Returns:
            最终改进后的回答
        """
        logger.info(format_log_message(f"🎯 开始处理问题: {question[:50]}..."))

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self._build_system_prompt()}
        ]

        messages.append({"role": "user", "content": f"问题：{question}\n\n请直接回答这个问题。"})

        response = self.model.think(messages)
        logger.info(format_log_message(f"📝 初始回答: {response[:100]}..."))

        messages.append({"role": "assistant", "content": response})

        for iteration in range(self.max_iterations):
            logger.info(format_log_message(f"🔄 第 {iteration + 1} 轮反思"))

            messages.append({
                "role": "user",
                "content": self._build_reflection_prompt(response)
            })

            reflection = self.model.think(messages)
            logger.info(format_log_message(f"💭 反思: {reflection[:100]}..."))

            messages.append({"role": "assistant", "content": reflection})

            if self._should_stop(reflection):
                final_answer = self._extract_final_answer(response)
                logger.info(format_log_message(f"✅ 反思判断停止，返回最终答案: {final_answer[:50]}..."))
                return final_answer

            messages.append({
                "role": "user",
                "content": self._build_improve_prompt(response, reflection)
            })

            response = self.model.think(messages)
            logger.info(format_log_message(f"📝 改进后回答: {response[:100]}..."))

            messages.append({"role": "assistant", "content": response})

        logger.info(format_log_message(f"⚠️ 达到最大迭代次数 {self.max_iterations}"))
        return response

    def _build_system_prompt(self) -> str:
        return """你是一个智能助手，善于通过反思来改进自己的回答。

你的工作流程：
1. 回答用户的问题
2. 反思自己的回答是否正确、完整、清晰
3. 如果发现问题，改进回答
4. 重复步骤 2-3 直到满意

在每轮反思中，你需要：
- 评估当前回答的质量
- 识别可能的问题或不足
- 决定是否需要改进

重要：
- 只有在回答已经完善、无需改进时才输出 "FINAL ANSWER"
- 如果需要改进，继续输出改进后的回答"""

    def _build_reflection_prompt(self, response: str) -> str:
        return f"""请反思以下回答：

---
{response}
---

请评估这个回答的质量：
1. 回答是否正确？
2. 回答是否完整？
3. 回答是否清晰？
4. 是否有遗漏或错误？

如果你认为回答已经足够好，无需改进，请输出：
FINAL ANSWER: 你认为完善的最终回答内容

如果需要改进，请输出你的反思意见，并给出改进后的回答。"""

    def _build_improve_prompt(self, response: str, reflection: str) -> str:
        return f"""基于以下反思意见，请改进你的回答。

原始回答：
---
{response}
---

反思意见：
---
{reflection}
---

请直接输出改进后的回答，不要重复反思过程。"""

    def _should_stop(self, reflection: str) -> bool:
        reflection_lower = reflection.lower().strip()
        if "final answer" in reflection_lower and ":" in reflection_lower:
            return True
        if reflection_lower.startswith("final answer"):
            return True
        if "无需改进" in reflection or "已经足够好" in reflection:
            return True
        return False

    def _extract_final_answer(self, content: str) -> str:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "final answer" in line.lower():
                if ":" in line:
                    return line.split(":", 1)[1].strip()
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        return content.strip()
