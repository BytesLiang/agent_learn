"""AutoGen 多代理系统实现.

四个智能体协作完成软件开发任务：
- ProductManager: 产品经理，将需求转化为开发计划
- Engineer: 工程师，编写代码
- CodeReviewer: 代码审查员，审查代码质量
- UserProxy: 用户代理，发起任务并验证
"""

import os

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

from src.utils.log import format_log_message, get_logger

logger = get_logger(__name__)


def create_model_client() -> OpenAIChatCompletionClient:
    """创建 AutoGen 使用的模型客户端."""
    return OpenAIChatCompletionClient(
        model=os.getenv("MODEL_ID", "qwen-plus"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.getenv("API_KEY", ""),
        model_info={
            "json_output": True,
            "function_calling": True,
            "vision": False,
            "family": "qwen",
            "structured_output": False,
        },
    )


def create_software_team(
    model_client: OpenAIChatCompletionClient,
) -> RoundRobinGroupChat:
    """创建软件工程团队（四个智能体协作）.

    Args:
        model_client: 模型客户端

    Returns:
        团队聊天对象
    """
    product_manager = AssistantAgent(
        name="ProductManager",
        model_client=model_client,
        system_message="""你是一个专业的产品经理。
        
你的职责：
1. 分析用户的需求，将其转化为清晰、可执行的开发计划
2. 将开发计划拆分为具体的任务步骤
3. 明确每个任务的技术要求和验收标准

输出格式：
## 开发计划
### 需求分析
[对用户需求的理解和澄清]

### 任务列表
1. [任务1描述]
2. [任务2描述]
...

### 验收标准
- [标准1]
- [标准2]""",
    )

    engineer = AssistantAgent(
        name="Engineer",
        model_client=model_client,
        system_message="""你是一个专业的软件工程师。

你的职责：
1. 根据产品经理的开发计划编写代码
2. 确保代码实现完整、功能正确
3. 编写清晰的代码注释和文档

注意事项：
- 优先实现核心功能
- 代码要简洁、可读
- 如果需要使用外部库，确保在代码中说明""",
    )

    code_reviewer = AssistantAgent(
        name="CodeReviewer",
        model_client=model_client,
        system_message="""你是一个专业的代码审查员。

你的职责：
1. 审查工程师提交的代码质量
2. 检查代码的正确性、可读性和健壮性
3. 提出具体的改进建议

审查维度：
- 功能完整性：是否满足需求？
- 代码质量：命名、注释、结构是否良好？
- 错误处理：是否有完善的异常处理？
- 安全性：是否有安全漏洞？

输出格式：
## 代码审查报告
### 优点
- [优点1]
- [优点2]

### 问题
- [问题1及建议修复方式]
- [问题2及建议修复方式]

### 结论
✅ 通过 / ❌ 需要修改""",
    )

    user_proxy = UserProxyAgent(
        name="UserProxy",
        description="""你是一个用户代理，负责以下职责：
1. 代表用户提出开发需求
2. 执行最终的代码实现
3. 验证功能是否符合预期
4. 提供用户反馈和建议

完成测试后请回复 TERMINATE。""",
    )

    team = RoundRobinGroupChat(
        participants=[product_manager, engineer, code_reviewer, user_proxy],
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=20,
    )

    return team


async def run_software_task(task: str) -> str:
    """运行软件开发任务.

    Args:
        task: 用户描述的任务

    Returns:
        最终结果

    Raises:
        ValueError: 任务描述为空
        Exception: 团队执行失败
    """
    if not task or not task.strip():
        logger.error(format_log_message("任务描述为空"))
        raise ValueError("任务描述不能为空")

    logger.info(format_log_message(f"开始执行任务: {task[:50]}..."))

    model_client = create_model_client()
    try:
        team = create_software_team(model_client)

        result = await Console(team.run_stream(task=task))
        logger.info(format_log_message("任务执行完成"))
        return str(result)
    except Exception as e:
        logger.error(format_log_message(f"任务执行失败: {e}"))
        raise
    finally:
        if model_client:
            await model_client.close()
