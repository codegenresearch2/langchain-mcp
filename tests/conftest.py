import pytest\nfrom langchain_tests.integration_tests import ToolsIntegrationTests\\\\\n@pytest.mark.usefixtures("mcptool")\nclass TestMCPToolIntegration(ToolsIntegrationTests):\n    @property\n    def tool_constructor(self):\n        return self.tool\n\n    @property\n    def tool_invoke_params_example(self) -> dict:\n        return {"path": "LICENSE"}\n\n# Copyright (C) 2024 Andrew Wason\n# SPDX-License-Identifier: MIT\nimport pytest\nfrom langchain_tests.unit_tests import ToolsUnitTests\n\n@pytest.mark.usefixtures("mcptool")\nclass TestMCPToolUnit(ToolsUnitTests):\n    @property\n    def tool_constructor(self):\n        return self.tool\n\n    @property\n    def tool_invoke_params_example(self) -> dict:\n        return {"path": "LICENSE"}\n\n# Copyright (C) 2024 Andrew Wason\n# SPDX-License-Identifier: MIT\nimport pytest\nfrom unittest import mock\nfrom langchain_tests.integration_tests import ToolsIntegrationTests\nfrom mcp import ClientSession, ListToolsResult, Tool\nfrom mcp.types import CallToolResult, TextContent\nfrom langchain_mcp import MCPToolkit\n\n@pytest.fixture(scope="class")\nasync def mcptoolkit(request):\n    session_mock = mock.AsyncMock(spec=ClientSession)\n    session_mock.list_tools.return_value = ListToolsResult(\n        tools=[\n            Tool(\n                name="read_file",\n                description=(\n                    "Read the complete contents of a file from the file system. Handles various text encodings "\n                    "and provides detailed error messages if the file cannot be read. "\n                    "Use this tool when you need to examine the contents of a single file. "\n                    "Only works within allowed directories."\n                ),\n                inputSchema={\n                    "type": "object",\n                    "properties": {"path": {"type": "string"}}, \n                    "required": ["path"],\n                    "additionalProperties": False,\n                    "$schema": "http://json-schema.org/draft-07/schema#",\n                }\n            )\n        ]\n    )\n    session_mock.call_tool.return_value = CallToolResult(\n        content=[TextContent(type="text", text="MIT License\n\nCopyright (c) 2024 Andrew Wason\n")], \n        isError=False\n    )\n    toolkit = MCPToolkit(session=session_mock)\n    await toolkit.initialize()\n    yield toolkit\n    if issubclass(request.cls, ToolsIntegrationTests):\n        session_mock.call_tool.assert_called_with("read_file", arguments={"path": "LICENSE"})\n\n@pytest.fixture(scope="class")\nasync def mcptool(request, mcptoolkit):\n    tool = (await mcptoolkit.get_tools())[0]\n    request.cls.tool = tool\n    yield tool\n