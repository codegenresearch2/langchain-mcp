# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

from unittest import mock
import pytest
from langchain_tests.integration_tests import ToolsIntegrationTests
from mcp import ClientSession, ListToolsResult, Tool
from mcp.types import CallToolResult, TextContent
from langchain_mcp import MCPToolkit

@pytest.fixture(scope="class")
def mcptoolkit():
    session_mock = mock.AsyncMock(spec=ClientSession)
    session_mock.list_tools.return_value = ListToolsResult(
        tools=[
            Tool(
                name="read_file",
                description=(
                    "Read the complete contents of a file from the file system. "
                    "Handles various text encodings and provides detailed error messages if the file cannot be read. "
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
    return MCPToolkit(session=session_mock)

@pytest.fixture(scope="class")
async def mcptool(request, mcptoolkit):
    try:
        tool = (await mcptoolkit.get_tools())[0]
        request.cls.tool = tool
        yield tool
    except IndexError:
        pytest.fail("No tools available in the toolkit. Please ensure toolkit is initialized.")

async def invoke_tool(tool, params):
    try:
        return await tool.invoke(params)
    except Exception as e:
        pytest.fail(f"Failed to invoke tool: {str(e)}")


In the rewritten code, the `mcptoolkit` fixture is initialized outside the test case to follow the rule of initializing tools before usage. Error handling has been added to handle uninitialized toolkits, and the tool invocation logic has been separated into a function `invoke_tool`.