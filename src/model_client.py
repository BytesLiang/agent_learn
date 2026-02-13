"""模型调用客户端."""
import logging
import os
from datetime import datetime

import dotenv
from openai import OpenAI

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


def _format_message(msg: str) -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"


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

        logger.info(_format_message(f"🚀 初始化成功，使用模型: {self.model_id}"))

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=30,
        )

    def think(self, messages: list[dict]) -> str:
        """调用模型生成响应（非流式）.

        Args:
            messages: 对话消息列表

        Returns:
            模型生成的文本响应

        Raises:
            Exception: API 调用失败时抛出
        """
        user_content = next((m["content"][:50] + "..." if len(m["content"]) > 50 else m["content"] for m in messages if m["role"] == "user"), "")
        logger.info(_format_message(f"💬 think: {user_content}"))

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
            )
            content = response.choices[0].message.content or ""
            logger.info(_format_message(f"✅ think 完成，响应长度: {len(content)} 字符"))
            return content
        except Exception as e:
            logger.error(_format_message(f"❌ think 失败: {e}"))
            raise

    def think_stream(self, messages: list[dict]) -> str:
        """调用模型生成响应（流式）.

        Args:
            messages: 对话消息列表

        Returns:
            模型生成的完整文本响应

        Raises:
            Exception: API 调用失败时抛出
        """
        user_content = next((m["content"][:50] + "..." if len(m["content"]) > 50 else m["content"] for m in messages if m["role"] == "user"), "")
        logger.info(_format_message(f"💬 think_stream: {user_content}"))

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                stream=True,
            )

            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                collected_content.append(content)

            full_content = "".join(collected_content)
            logger.info(_format_message(f"✅ think_stream 完成，响应长度: {len(full_content)} 字符"))
            return full_content
        except Exception as e:
            logger.error(_format_message(f"❌ think_stream 失败: {e}"))
            raise
