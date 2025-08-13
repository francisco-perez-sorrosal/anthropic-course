# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package implementing document-related tools for converting and processing document formats. The package exposes tools through an MCP (Model Control Protocol) server interface for seamless integration with AI assistants.

## Architecture

- **MCP Server**: Uses FastMCP framework for tool registration and server implementation
- **Tools Module**: Contains individual tool implementations (`tools/math.py`, `tools/document.py`)
- **Entry Point**: `main.py` initializes the MCP server and registers tools
- **Document Processing**: Uses MarkItDown library for document format conversion (DOCX, PDF)

## Development Commands

### Setup
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install package in development mode
uv pip install -e .
```

### Running the Server
```bash
# Start the MCP server
uv run main.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_document.py
```

## Tool Development

Tools are defined as Python functions and registered with the MCP server:

```python
mcp.tool()(my_function)
```

### Tool Definition Guidelines

Tool descriptions should:

- Begin with a one-line summary
- Provide detailed explanation of functionality
- Explain when to use (and not use) the tool
- Include usage examples with expected input/output

### Parameter Definitions

Use `Field` from pydantic for parameter descriptions:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does")
) -> ReturnType:
    """Comprehensive docstring here
    
    Takes detailed inputs and returns processed output. This tool handles
    specific use cases and operations.
    
    When to use:
    - When you need to perform specific operation
    - When you need precise processing
    
    Examples:
    >>> my_tool("input", 42)
    expected_output
    """
    # Implementation
```

### Tool Registration

Example tool registration in `main.py`:

```python
from mcp.server.fastmcp import FastMCP
from tools.my_tool import my_function

mcp = FastMCP("server_name")
mcp.tool()(my_function)
```

## Dependencies

Key dependencies managed through pyproject.toml:

- `mcp[cli]==1.8.0` - MCP server framework
- `markitdown[docx,pdf]>=0.1.1` - Document conversion
- `pydantic>=2.11.3` - Type validation and parameter descriptions
- `pytest>=8.3.5` - Testing framework

## Best Practices

- Always apply appropriate types to function args

### Python Project Best Practices for PoCs

- Use `uv` (or `pip`) for dependency management
- Create and use virtual environments
- Use `pyproject.toml` for project configuration
- Implement basic type hints
- Write minimal but meaningful docstrings
- Use `pytest` for testing
- Follow PEP8 style guidelines
- Use `ruff` or `black` for code formatting
- Keep dependencies minimal and pinned to specific versions
- Use `typing` module for type annotations
- Include a basic `.gitignore` file

### Type Annotation Best Practices

- Prioritize use pydantic types combined with typing types when necessary