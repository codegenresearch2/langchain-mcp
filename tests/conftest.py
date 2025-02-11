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

    # Assertions in the fixture
    assert session_mock.call_tool.called, "The `call_tool` method was not called"
    assert session_mock.call_tool.call_count == 1, "The `call_tool` method was called more than once"
    assert session_mock.call_tool.call_args[1]['tool'] == "read_file" and session_mock.call_tool.call_args[1]['arguments'] == {"path": "LICENSE"}, "The `call_tool` method was not called with the correct arguments"


@pytest.fixture(scope="class")
async def mcptool(request, mcptoolkit):
    await mcptoolkit.initialize()  # Initialization method call
    tools = await mcptoolkit.get_tools()
    if not tools:
        pytest.fail("No tools available")
    request.cls.tool = tools[0]
    yield request.cls.tool

    # Assertions in the fixture
    assert request.cls.tool.name == "read_file", "The tool retrieved is not the expected tool"


@pytest.mark.usefixtures("mcptoolkit")
class TestMCPToolIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self):
        return self.tool

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"path": "LICENSE"}


@pytest.mark.usefixtures("mcptoolkit")
class TestMCPToolUnit(ToolsIntegrationTests):
    @property
    def tool_constructor(self):
        return self.tool

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"path": "LICENSE"}