# Agent Learn - Development Guidelines

## Project Overview

This is a Python project for learning and experimenting with AI agents. The project is in its initial setup phase with no existing code yet.

## Language and Style

- Always reply in Simplified Chinese
- Direct answers without unnecessary pleasantries
- Use Chinese for code comments

## Build, Lint, and Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python -m src
```

### Linting and Formatting
```bash
ruff check .                    # Run ruff linter
ruff check --fix .              # Auto-fix linting issues
black .                         # Format code with black
black --check .                 # Check formatting without changes
isort --check-only --diff .     # Check import sorting
mypy src/                       # Type checking with mypy
```

### Testing
```bash
pytest                          # Run all tests
pytest -v                       # Run tests with verbose output
pytest tests/                   # Run tests in tests directory
pytest -k "test_name"           # Run specific test by name
pytest --tb=short               # Short traceback on failures
pytest -x                       # Stop on first failure
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
- Define custom types using `TypeAlias` or `TypedDict` when beneficial
- Use generics (`List[T]`, `Dict[K, V]`) for container types

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

### Code Organization
- Keep functions small and focused (single responsibility)
- Maximum function length: ~50 lines
- Use descriptive variable and function names
- Extract repeated code into reusable functions
- Keep related code together in modules
- Use `__init__.py` to mark packages and control exports

### Documentation
- Use docstrings for all public functions, classes, and modules
- Follow Google or NumPy docstring format
- Include docstring for private methods when complex
- Update docstrings when modifying code

### Async Code
- Use `async/await` for I/O-bound operations
- Use `asyncio` for concurrent operations
- Avoid blocking calls in async functions
- Set appropriate timeouts for async operations

## Working Habits

- Read related files before making changes
- Ask for clarification when uncertain
- Make minimal necessary changes per modification
- Run linting and tests after making changes
- Commit changes in logical, atomic units
- Write tests before or alongside new features
- Review existing code to understand patterns before adding new code

## AI Agent Specific Guidelines

### Interacting with AI Models
- Store API keys in `.env` files, never commit them
- Use environment variables for model configuration
- Implement proper error handling for API rate limits
- Add retry logic with exponential backoff for API calls
- Log model inputs and outputs for debugging (respect privacy)
- Consider using LangChain or similar frameworks for flexibility

### Agent Design Patterns
- Implement clear separation between agent logic and tools
- Use structured outputs when available (JSON mode)
- Implement proper prompting techniques
- Consider context window limitations
- Add human-in-the-loop for sensitive operations
- Implement proper feedback mechanisms

### Testing AI Agents
- Test prompts in isolation
- Mock external API calls in unit tests
- Test error handling and edge cases
- Use evaluation frameworks for quality assessment
- Implement integration tests for agent workflows

## Dependencies Management

- Add new dependencies to `requirements.txt` with versions
- Pin versions for critical dependencies
- Use `pip-compile` for reproducible builds
- Review dependencies for security vulnerabilities regularly
- Update dependencies periodically but carefully

## File Structure

```
agent-learn/
├── src/                 # Source code
├── tests/               # Test files (create when adding code)
├── docs/                # Documentation and notes
├── requirements.txt     # Dependencies
├── README.md           # Project documentation
├── AGENTS.md           # This file
├── .env                # Environment variables (not committed)
└── .gitignore          # Git ignore rules
```
