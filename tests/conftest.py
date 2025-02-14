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
    request.cls.toolkit = toolkit
    yield toolkit

@pytest.fixture(scope="class")
async def mcptool(request):
    toolkit = getattr(request.cls, 'toolkit', None)
    if toolkit is None:
        raise ValueError("Toolkit is not initialized. Make sure to initialize tools before usage.")

    tools = await toolkit.get_tools()
    if not tools:
        raise ValueError("No tools are available in the toolkit.")

    tool = tools[0]
    request.cls.tools = tools
    yield tool