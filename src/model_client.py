"""模型调用客户端."""
import os
from typing import Any

from openai import OpenAI

from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class ModelClient:
    """大模型 API 调用客户端."""

    def __init__(self) -> None:
        """从环境变量初始化配置."""
        self.api_key: str = os.getenv("API_KEY", "")
        self.model_id: str = os.getenv("MODEL_ID", "")
        self.api_url: str = os.getenv("API_URL", "")

        if not self.api_key:
            raise ValueError("API_KEY 未配置")
        if not self.model_id:
            raise ValueError("MODEL_ID 未配置")
        if not self.api_url:
            raise ValueError("API_URL 未配置")

        logger.info(format_log_message(f"🚀 初始化成功，使用模型: {self.model_id}"))

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=30,
        )

    def _get_user_content(self, messages: list[dict[str, Any]]) -> str:
        for m in messages:
            if m.get("role") == "user":
                content = m.get("content", "")
                return content[:50] + "..." if len(content) > 50 else content
        return ""

    def think(self, messages: list[dict[str, Any]], stream: bool = False) -> str:
        """调用模型生成响应.

        Args:
            messages: 对话消息列表
            stream: 是否使用流式输出，默认 False

        Returns:
            模型生成的文本响应

        Raises:
            Exception: API 调用失败时抛出
        """
        user_content = self._get_user_content(messages)
        mode = "think_stream" if stream else "think"
        logger.info(format_log_message(f"💬 {mode}: {user_content}"))

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,  # type: ignore[arg-type]
                stream=stream,
            )

            if stream:
                collected_content = []
                try:
                    for chunk in response:  # type: ignore[union-attr]
                        content = chunk.choices[0].delta.content or ""  # type: ignore[union-attr]
                        collected_content.append(content)
                finally:
                    response.close()  # type: ignore[union-attr]

                full_content = "".join(collected_content)
                logger.info(format_log_message(f"✅ {mode} 完成，响应长度: {len(full_content)} 字符"))
                return full_content
            else:
                content = response.choices[0].message.content or ""  # type: ignore[union-attr]
                logger.info(format_log_message(f"✅ {mode} 完成，响应长度: {len(content)} 字符"))
                return content

        except Exception as e:
            logger.error(format_log_message(f"❌ {mode} 失败: {e}"))
            raise
