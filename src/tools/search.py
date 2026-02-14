"""基于 SerpApi 的网页搜索引擎工具."""
import os

from serpapi import Client

from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


class WebSearchTool:
    """基于 SerpApi 的网页搜索引擎工具.

    优先寻找直接答案，如果没有直接答案则返回前三个有机结果的摘要。
    """

    name = "web_search"
    description = "搜索网页并返回结果。优先返回直接答案，如果没有则返回前三个网页摘要。"

    def __init__(self) -> None:
        self.api_key = os.getenv("SERPAPI_API_KEY", "")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY 未配置")
        self.client = Client(api_key=self.api_key)
        logger.info(format_log_message("🔍 WebSearchTool 初始化成功"))

    def execute(self, query: str) -> str:
        """执行网页搜索.

        Args:
            query: 搜索关键词

        Returns:
            搜索结果（直接答案或网页摘要）

        Raises:
            ValueError: 搜索关键词为空
        """
        if not query or not query.strip():
            raise ValueError("搜索关键词不能为空")

        logger.info(format_log_message(f"🔍 搜索: {query}"))

        try:
            params = {
                "engine": "google",
                "q": query,
            }

            results = self.client.search(params).as_dict()

            answer = self._extract_direct_answer(results)
            if answer:
                logger.info(format_log_message(f"✅ 找到直接答案，{len(answer)} 字符"))
                return answer

            snippets = self._extract_organic_snippets(results, top_n=3)
            if snippets:
                result = "\n\n".join(snippets)
                logger.info(format_log_message(f"✅ 返回 {len(snippets)} 个网页摘要，{len(result)} 字符"))
                return result

            logger.info(format_log_message("⚠️ 未找到任何结果"))
            return "未找到相关结果"

        except Exception as e:
            logger.error(format_log_message(f"❌ 搜索失败: {e}"))
            raise

    def _extract_direct_answer(self, results: dict) -> str:
        """从搜索结果中提取直接答案.

        Args:
            results: SerpApi 返回的搜索结果

        Returns:
            直接答案文本，如果没有则返回空字符串
        """
        if "answer_box" in results and results["answer_box"]:
            answer_box = results["answer_box"]
            if "answer" in answer_box:
                return answer_box["answer"]
            if "snippet" in answer_box:
                return answer_box["snippet"]

        if "featured_snippet" in results and results["featured_snippet"]:
            snippet = results["featured_snippet"]
            if "snippet" in snippet:
                return snippet["snippet"]

        return ""

    def _extract_organic_snippets(self, results: dict, top_n: int = 3) -> list[str]:
        """提取有机搜索结果的摘要.

        Args:
            results: SerpApi 返回的搜索结果
            top_n: 返回前 N 个结果

        Returns:
            网页摘要列表
        """
        top_n = min(max(top_n, 1), 10)

        snippets = []
        organic_results = results.get("organic_results", [])

        for item in organic_results[:top_n]:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")

            if title and snippet:
                snippets.append(f"{title}\n{snippet}\n{link}")

        return snippets
