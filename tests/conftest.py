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
async def selected_tool(mcptool):
    if not mcptool:
        raise ValueError("No tools available. Please initialize tools first.")
    return mcptool[0]

@pytest.mark.usefixtures("selected_tool")
class TestMCPToolIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self):
        return self.selected_tool

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"path": "LICENSE"}