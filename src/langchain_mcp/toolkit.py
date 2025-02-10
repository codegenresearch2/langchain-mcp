# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

import asyncio
import warnings
from collections.abc import Callable

import pydantic
import pydantic_core
import typing_extensions as t
from langchain_core.tools.base import BaseTool, BaseToolkit, ToolException
from mcp import ClientSession, ListToolsResult, Tool
from mcp.types import CallToolResult, TextContent


class MCPToolkit(BaseToolkit):
    """
    MCP server toolkit
    """

    session: ClientSession
    """The MCP session used to obtain the tools"""

    def __init__(self, session: ClientSession):
        self.session = session
        self._tools = None

    async def initialize(self) -> None:
        if self._tools is None:
            await self.session.initialize()
            self._tools = await self.get_tools()

    @t.override
    async def get_tools(self) -> ListToolsResult:  # type: ignore[override]
        if self._tools is None:
            raise RuntimeError("MCPToolkit has not been initialized.")
        return ListToolsResult(tools=[
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
        ])


def create_schema_model(schema: dict[str, t.Any]) -> type[pydantic.BaseModel]:
    class Schema(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="allow", arbitrary_types_allowed=True)

        @t.override
        @classmethod
        def model_json_schema(cls, by_alias: bool = True, ref_template: str = pydantic.json_schema.DEFAULT_REF_TEMPLATE) -> dict[str, t.Any]:
            return schema

    return Schema


class MCPTool(BaseTool):
    """
    MCP server tool
    """

    toolkit: MCPToolkit
    handle_tool_error: bool | str | Callable[[ToolException], str] | None = True

    @t.override
    def _run(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        warnings.warn(
            "Invoke this tool asynchronously using `ainvoke`. This method exists only to satisfy tests.", stacklevel=1
        )
        return asyncio.run(self._arun(*args, **kwargs))

    @t.override
    async def _arun(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        result = await self.toolkit.session.call_tool(self.name, arguments=kwargs)
        content = pydantic_core.to_json(result.content).decode()
        if result.isError:
            raise ToolException(content)
        return content

    @t.override
    @property
    def tool_call_schema(self) -> type[pydantic.BaseModel]:
        assert self.args_schema is not None  # noqa: S101
        return self.args_schema