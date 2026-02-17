"""测试 AutoGen 多代理系统."""
import asyncio

from src.agents.autogen_team import run_software_task


async def test_autogen_team():
    """测试 AutoGen 多代理系统."""
    print("=== AutoGen 多代理系统测试 ===\n")

    task = "帮我写一个计算器程序，支持加减乘除运算"

    print(f"任务: {task}")
    print("-" * 50)

    result = await run_software_task(task)
    print(f"\n最终结果:\n{result}")


if __name__ == "__main__":
    asyncio.run(test_autogen_team())
