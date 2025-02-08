import pytest\nfrom unittest import mock\nfrom mcp import ClientSession, ListToolsResult, Tool\nfrom mcp.types import CallToolResult, TextContent\nfrom langchain_mcp import MCPToolkit\n\n\n@pytest.fixture(scope='class')\ndef mcptoolkit(request):\n    session_mock = mock.Mock(spec=ClientSession)\n    session_mock.list_tools.return_value = ListToolsResult(\n        tools=[\n            Tool(\n                name='read_file',\n                description='Read the complete contents of a file from the file system. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Only works within allowed directories.',\n                inputSchema={\n                    'type': 'object',\n                    'properties': {'path': {'type': 'string'}}, \n                    'required': ['path'], \n                    'additionalProperties': False, \n                    '$schema': 'http://json-schema.org/draft-07/schema#', \n                }\n            ) \n        ]\n    )\n    session_mock.call_tool.return_value = CallToolResult(\n        content=[TextContent(type='text', text='MIT License\n\nCopyright (c) 2024 Andrew Wason\n')], \n        isError=False\n    )\n    toolkit = MCPToolkit(session=session_mock)\n    yield toolkit\n\n\n@pytest.fixture(scope='class')\nasync def mcptool(request, mcptoolkit):\n    tool = (await mcptoolkit.get_tools())[0]\n    request.cls.tool = tool\n    yield tool