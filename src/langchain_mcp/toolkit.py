import asyncio\\\nimport warnings\\\nfrom typing import Any, Callable, Optional\\\\nimport pydantic\\\\\nimport pydantic_core\\\\\nimport typing_extensions as t\\\\nfrom langchain_core.tools.base import BaseTool, BaseToolkit, ToolException\\\\nfrom mcp import ClientSession, ListToolsResult, Tool\\\\n\\\\nclass MCPToolkit(BaseToolkit):\\\\