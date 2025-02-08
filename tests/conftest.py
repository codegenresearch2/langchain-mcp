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
                description='Read the complete contents of a file from the file system. Handles various text encodings '\n                    'and provides detailed error messages if the file cannot be read. '\n                    'Use this tool when you need to examine the contents of a single file. '\n                    'Only works within allowed directories.'\n                ),
            )
        ]
    )
    session_mock.call_tool.return_value = CallToolResult(
        content=[TextContent(type='text', text='MIT License\n\nCopyright (c) 2024 Andrew Wason\n')], isError=False)
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