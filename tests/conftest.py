import pytest\\\nfrom unittest import mock\\\\nfrom langchain_tests.integration_tests import ToolsIntegrationTests\\\\nfrom mcp import ClientSession, ListToolsResult, Tool\\\\nfrom mcp.types import CallToolResult, TextContent\\\\nfrom langchain_mcp import MCPToolkit\\\\\n@pytest.fixture(scope='class')\\\ndef mcptoolkit(request):\\\\\nsession_mock = mock.AsyncMock(spec=ClientSession)\\\\\nsession_mock.list_tools.return_value = ListToolsResult(\\\n    tools=[\\\\\n        Tool(\\\n            name='read_file',\\\\\n            description=(\\\n                'Read the complete contents of a file from the file system. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Only works within allowed directories.'\\\\\n            ),\\\\\n            inputSchema={\\\n                'type': 'object',\\\\\n                'properties': {'path': {'type': 'string'}}, \\\\\n                'required': ['path'], \\\\\n                'additionalProperties': False,\\\\\n                '$schema': 'http://json-schema.org/draft-07/schema#',\\\\\n            }\\\\\n        )\\\\\n    ]\\\\\n)\\\\\nsession_mock.call_tool.return_value = CallToolResult(\\\n    content=[TextContent(type='text', text='MIT License\\\\\n\nCopyright (c) 2024 Andrew Wason\\\\\n')], \\\\\n    isError=False\\\\\n)\\\\\ntoolkit = MCPToolkit(session=session_mock)\\\\\nyield toolkit\\\\\nif issubclass(request.cls, ToolsIntegrationTests):\\\\\n    assert session_mock.call_tool.assert_called_with("read_file", arguments={'path': 'LICENSE'})\\\n}