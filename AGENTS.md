# Agent Learn - 开发指南

## 项目概述

Python 项目，用于学习和实验 AI Agent 模式，包括 ReAct、Plan-and-Solve、Reflection、AutoGen 多代理团队以及 LangGraph 问答助手。

## 语言和风格

- 与用户交流时使用简体中文
- 代码注释用中文
- 直接回答问题，不要客套话

## 构建、测试、代码检查命令

### 安装
```bash
pip install -r requirements.txt
```

### 运行
```bash
python -m src                    # 运行主模块
python test_react.py            # 运行单个测试文件
python test_langgraph_qa.py     # 测试 LangGraph 问答助手
```

### 代码检查和格式化
```bash
ruff check . && ruff check --fix .  # 检查并自动修复
black .                          # 格式化代码
black --check .                  # 检查格式
isort --check-only --diff .      # 检查 import 顺序
mypy src/ --ignore-missing-imports  # 类型检查
```

### 测试
```bash
pytest                           # 运行所有测试
pytest -v                        # 详细输出
pytest test_react.py             # 运行单个测试文件
pytest -k "test_name"            # 按名称运行特定测试
pytest -x                        # 首次失败后停止
pytest --tb=short                # 简短错误信息
```

## 代码风格

### Import
- 使用绝对导入：`from package import module`
- 分组顺序：标准库 > 第三方 > 本地应用
- 组内按字母排序
- 避免 `from module import *`

### 格式
- 4 空格缩进
- 最大行长度 100 字符
- 函数、类之间用空行分隔
- 运算符和逗号后保持一致间距
- 无尾部空白

### 类型
- 所有函数参数和返回值使用类型提示
- 尽量避免 `Any`
- 使用 `Optional[T]` 而非 `T | None`
- 使用泛型 `List[T]`, `Dict[K, V]`
- 外部库可加 `# type: ignore`

### 命名
- 文件：snake_case (`my_module.py`)
- 类：CamelCase (`MyClass`)
- 函数/变量：snake_case (`my_function`)
- 常量：UPPER_SNAKE_CASE (`MY_CONSTANT`)
- 私有方法/变量：前缀 `_` (`_private_method`)
- 避免单字符命名（计数器除外）

### 错误处理
- 使用具体异常 (`ValueError`, `FileNotFoundError` 等)
- 不随意捕获 `Exception`
- 提供有意义的错误信息
- 优先验证而非异常捕获
- 使用适当级别的日志记录
- 让异常在调用者需要处理时传播

### 日志
- 使用 `src/utils/log.py` 中的共享工具
- 用 `get_logger(__name__)` 创建 logger
- 用 `format_log_message()` 保持时间戳格式一致
- 日志包含上下文信息

## 项目结构

```
agent-learn/
├── src/
│   ├── __init__.py              # 加载 dotenv
│   ├── __main__.py              # 入口点
│   ├── model_client.py           # LLM API 客户端
│   ├── agents/
│   │   ├── react.py             # ReAct Agent
│   │   ├── plan_and_solve.py    # Plan-and-Solve Agent
│   │   ├── reflection.py        # Reflection Agent
│   │   ├── autogen_team.py      # AutoGen 多代理团队
│   │   └── langgraph_qa/        # LangGraph 问答助手
│   │       ├── __init__.py
│   │       ├── agent.py         # 主 Agent 实现
│   │       ├── states.py        # 状态定义
│   │       └── nodes/           # 三阶段节点
│   │           ├── understand.py  # 理解阶段
│   │           ├── search.py      # 搜索阶段（Tavily API）
│   │           └── answer.py      # 回答阶段
│   ├── tools/
│   │   ├── registry.py          # 工具注册和执行器
│   │   └── search.py            # Web 搜索工具
│   └── utils/
│       └── log.py                # 日志工具
├── test_*.py                    # 根目录测试文件
├── requirements.txt
├── .env                         # 环境变量（不提交）
└── .gitignore
```

## Agent 实现模式

### 工具接口
```python
class Tool:
    name: str
    description: str
    execute(**kwargs) -> str
```

### 工具注册
```python
registry = ToolRegistry()
registry.register(WebSearchTool())
result = registry.execute("web_search", query="...")
```

### Agent 模式
- **ReAct**：交替推理和执行，适合需要多步推理的问题
- **Plan-and-Solve**：先创建计划，再逐步执行，适合复杂任务分解
- **Reflection**：迭代反思和改进输出，适合需要高质量输出的任务
- **AutoGen 多代理团队**：多角色协作，适合软件开发等复杂任务
- **LangGraph 问答助手**：三阶段流程（理解→搜索→回答），适合问答场景
  - 理解阶段：意图识别、实体提取
  - 搜索阶段：Tavily API 实时搜索
  - 回答阶段：基于搜索结果生成回答

## 工作习惯

- 修改前先阅读相关文件
- 不确定时先问
- 每次做最小必要修改
- 修改后运行 lint 和测试
- 以逻辑原子单位提交
- 新功能编写测试
- 添加新代码前先了解现有模式

## 依赖管理

- 新依赖添加到 `requirements.txt`（带版本，如 `package>=1.0.0`）
- 关键依赖固定版本
- 定期检查安全漏洞
- 当前依赖：
  - python-dotenv, openai, serpapi
  - autogen-agentchat, autogen-ext
  - langgraph, langchain-core
  - tavily-python

## 配置

### 环境变量 (.env)
```bash
# 大模型 API 配置
API_KEY=your_api_key
MODEL_ID=qwen-plus
API_URL=https://...

# SerpApi 搜索
SERPAPI_API_KEY=your_key

# Tavily 搜索 API（用于 LangGraph 问答助手）
TAVILY_API_KEY=your_tavily_key
```

### 获取 Tavily API Key
1. 访问 https://tavily.com 注册账号
2. 在 Dashboard 获取 API Key
3. 每月免费 1000 次搜索

## 测试指南

- 隔离测试 prompt
- 单元测试尽量 mock 外部 API
- 测试错误处理和边界情况
- 集成测试覆盖完整工作流
- 测试成功和失败场景
- Agent 错误处理：优雅处理工具执行错误、记录上下文信息、向 agent 返回有意义的错误信息、实现瞬时失败重试、设置适当的 API 超时

## LangGraph 问答助手使用示例

```python
from src.agents.langgraph_qa import LangGraphQAAgent
from src.model_client import ModelClient

model_client = ModelClient()
agent = LangGraphQAAgent(model_client)

# 简单模式
answer = agent.run("Python 的创始人是谁？")

# 详细模式（返回完整状态）
result = agent.run_with_details("为什么 Python 如此流行？")
print(result["intent_analysis"])  # 意图分析结果
print(result["search_results"])   # 搜索结果
print(result["final_answer"])     # 最终回答
```
