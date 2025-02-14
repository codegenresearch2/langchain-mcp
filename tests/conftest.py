# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

from unittest import mock
import pytest
from langchain_tests.integration_tests import ToolsIntegrationTests
from mcp import ClientSession, ListToolsResult, Tool
from mcp.types import CallToolResult, TextContent
from langchain_mcp import MCPToolkit

@pytest.fixture(scope="class")
def mcptoolkit(request):
    session_mock = mock.AsyncMock(spec=ClientSession)
    session_mock.list_tools.return_value = ListToolsResult(
        tools=[
            Tool(
                name="read_file",
                description=(
                    "Read the complete contents of a file from the file system. Handles various text encodings "
                    "and provides detailed error messages if the file cannot be read. "
                    "Use this tool when you need to examine the contents of a single file. "
                    "Only works within allowed directories."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                    "additionalProperties": False,
                    "$schema": "http://json-schema.org/draft-07/schema#",
                },
            )
        ]
    )
    session_mock.call_tool.return_value = CallToolResult(
        content=[TextContent(type="text", text="MIT License\n\nCopyright (c) 2024 Andrew Wason\n")],
        isError=False,
    )
    toolkit = MCPToolkit(session=session_mock)
    yield toolkit

@pytest.fixture(scope="class")
async def mcptool(request, mcptoolkit):
    tools = await mcptoolkit.get_tools()
    if not tools:
        raise ValueError("No tools initialized in the toolkit.")
    request.cls.tools = tools
    yield tools

@pytest.fixture(scope="class")
def selected_tool(request, mcptool):
    if not hasattr(request.cls, 'tools') or not request.cls.tools:
        raise ValueError("No tools available for selection.")
    tool = request.cls.tools[0]
    yield tool


In this rewritten code, I have initialized the tools before usage and handled them as a list. I have also added clearer error handling for uninitialized tools. If no tools are initialized in the toolkit or if no tools are available for selection, a ValueError is raised with an appropriate error message.