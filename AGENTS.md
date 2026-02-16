# Agent Learn - Development Guidelines

## Project Overview

This is a Python project for learning and experimenting with AI agents. The project implements various agent patterns including ReAct and Plan-and-Solve.

## Language and Style

- Always reply in Simplified Chinese when communicating with users
- Direct answers without unnecessary pleasantries
- Use Chinese for code comments

## Build, Lint, and Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python -m src                    # Run main module
python test_model_client.py       # Run individual test files
python test_tools.py
python test_react.py
python test_plan_and_solve.py
```

### Linting and Formatting
```bash
ruff check .                     # Run ruff linter
ruff check --fix .               # Auto-fix linting issues
black .                          # Format code with black
black --check .                  # Check formatting without changes
isort --check-only --diff .      # Check import sorting
mypy src/                       # Type checking with mypy
mypy src/ --ignore-missing-imports  # Ignore missing stubs (e.g., serpapi)
```

### Testing
```bash
pytest                           # Run all tests
pytest -v                        # Run tests with verbose output
pytest tests/                    # Run tests in tests directory
pytest test_*.py                 # Run tests matching pattern
pytest -k "test_name"           # Run specific test by name
pytest --tb=short                # Short traceback on failures
pytest -x                        # Stop on first failure
```

## Code Style Guidelines

### Imports
- Use absolute imports: `from package import module`
- Group imports in this order: standard library, third-party, local application
- Sort imports alphabetically within each group
- Use `isort` to maintain import order
- Avoid wildcard imports (`from module import *`)

### Formatting
- Use 4 spaces for indentation (PEP 8 standard)
- Maximum line length: 100 characters
- Use blank lines to separate functions, classes, and logical sections
- Use consistent spacing around operators and after commas
- No trailing whitespace

### Types
- Use type hints for all function parameters and return values
- Prefer explicit types over `Any` when possible
- Use `Optional[T]` instead of `T | None` for compatibility
- Use generics (`List[T]`, `Dict[K, V]`) for container types
- Add `# type: ignore[xxx]` comments when necessary for external libraries

### Naming Conventions
- **Files**: lowercase with underscores (`my_module.py`)
- **Classes**: CamelCase (`MyClass`)
- **Functions/variables**: snake_case (`my_function`, `my_variable`)
- **Constants**: UPPER_SNAKE_CASE (`MY_CONSTANT`)
- **Private methods/variables**: prefix with `_` (`_private_method`)
- **Avoid single-character names except for counters or iterators

### Error Handling
- Use specific exceptions (`ValueError`, `FileNotFoundError`, etc.)
- Don't catch generic `Exception` unless absolutely necessary
- Provide meaningful error messages
- Use `try/except` blocks sparingly; prefer validation
- Log errors with appropriate severity levels
- Let exceptions propagate when the caller should handle them

### Logging
- Use the shared logging utilities from `src/utils/log.py`
- Use `get_logger(__name__)` to create loggers
- Use `format_log_message()` for consistent timestamp formatting
- Include contextual information in log messages

## Project Structure

```
agent-learn/
├── src/
│   ├── __init__.py              # Main package init (loads dotenv)
│   ├── __main__.py              # Application entry point
│   ├── model_client.py           # LLM API client
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── react.py             # ReAct agent implementation
│   │   └── plan_and_solve.py    # Plan-and-Solve agent implementation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py          # Tool registry and executor
│   │   └── search.py            # Web search tool (SerpApi)
│   └── utils/
│       ├── __init__.py
│       └── log.py                # Shared logging utilities
├── tests/                       # Test directory (when added)
├── test_*.py                    # Individual test files in root
├── docs/                        # Documentation
├── requirements.txt             # Dependencies
├── README.md                    # Project documentation
├── AGENTS.md                    # This file
├── .env                         # Environment variables (not committed)
└── .gitignore                   # Git ignore rules
```

## Agent Implementation Patterns

### Tool Interface
Tools must implement the following interface:
```python
class Tool:
    name: str                    # Unique tool identifier
    description: str             # Tool description for LLM
    execute(**kwargs) -> str     # Execute tool with parameters
```

### Tool Registry
Use `ToolRegistry` to manage tools:
```python
registry = ToolRegistry()
registry.register(WebSearchTool())
result = registry.execute("web_search", query="...")
```

### Agent Patterns
- **ReAct**: Alternates between reasoning and action execution
- **Plan-and-Solve**: Creates plan first, then executes step by step

## Working Habits

- Read related files before making changes
- Ask for clarification when uncertain
- Make minimal necessary changes per modification
- Run linting and tests after making changes
- Commit changes in logical, atomic units
- Write tests before or alongside new features
- Review existing code to understand patterns before adding new code

## Dependencies Management

- Add new dependencies to `requirements.txt` with versions (e.g., `package>=1.0.0`)
- Pin versions for critical dependencies
- Review dependencies for security vulnerabilities regularly
- Update dependencies periodically but carefully
- Current dependencies:
  - `python-dotenv>=1.0.0` - Environment variable loading
  - `openai>=1.0.0` - LLM API client
  - `serpapi>=0.1.5` - Web search API

## Configuration

### Environment Variables (in .env)
```bash
API_KEY=your_api_key            # LLM API key
MODEL_ID=qwen-plus              # Model identifier
API_URL=https://...             # API base URL
SERPAPI_API_KEY=your_key       # SerpApi key for web search
```

## Testing AI Agents

- Test prompts in isolation
- Mock external API calls in unit tests when possible
- Test error handling and edge cases
- Use integration tests for full agent workflows
- Test both success and failure scenarios

## Error Handling in Agents

- Always handle tool execution errors gracefully
- Log errors with contextual information
- Return meaningful error messages to the agent
- Implement retry logic for transient failures
- Set appropriate timeouts for API calls
