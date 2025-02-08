import pytest
from unittest import mock
from mcp import ClientSession, ListToolsResult, Tool, CallToolResult, TextContent
from langchain_mcp import MCPToolkit


@pytest.fixture(scope='class')
def setup_mcptoolkit():
    session_mock = mock.AsyncMock(spec=ClientSession)
    session_mock.list_tools.return_value = ListToolsResult(
        tools=[
            Tool(
                name='read_file',
                description=(
                    'Read the complete contents of a file from the file system. Handles various text encodings '\\
                    'and provides detailed error messages if the file cannot be read. '\\
                    'Use this tool when you need to examine the contents of a single file. '\\
                    'Only works within allowed directories.'\\
                ),
                inputSchema={
                    'type': 'object',
                    'properties': {'path': {'type': 'string'}},
                    'required': ['path'],
                    'additionalProperties': False,
                    '$schema': 'http://json-schema.org/draft-07/schema#',
                },
            )
        ]
    )
    session_mock.call_tool.return_value = CallToolResult(
        content=[TextContent(type='text', text='MIT License\\n\\nCopyright (c) 2024 Andrew Wason\\n')], isError=False)
    toolkit = MCPToolkit(session=session_mock)
    return toolkit


@pytest.fixture(scope='class')
async def mcptool(request):
    mcptoolkit = setup_mcptoolkit()
    await mcptoolkit.initialize()  # Ensure initialization before accessing tools
    tool = (await mcptoolkit.get_tools())[0]
    request.cls.tool = tool
    if issubclass(request.cls, ToolsIntegrationTests):
        session_mock.call_tool.assert_called_with('read_file', arguments={'path': 'LICENSE'})
    yield tool