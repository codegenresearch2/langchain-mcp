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

    _tools: ListToolsResult | None = None
    _initialized: bool = False

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, session: ClientSession):
        self.session = session

    async def initialize(self) -> None:
        """
        Initializes the MCPToolkit by listing tools and setting the _initialized flag.
        """
        if not self._initialized:
            await self.session.initialize()
            self._tools = await self.get_tools()
            self._initialized = True

    @t.override
    async def get_tools(self) -> ListToolsResult:  # type: ignore[override]
        """
        Retrieves the list of tools from the MCP session.
        """
        if self._tools is None:
            raise RuntimeError("MCPToolkit has not been initialized.")
        return self._tools


def create_schema_model(schema: dict[str, t.Any]) -> type[pydantic.BaseModel]:
    """
    Creates a Pydantic model from a JSON schema.
    """
    class Schema(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="allow", arbitrary_types_allowed=True)

        @t.override
        @classmethod
        def model_json_schema(cls, by_alias: bool = True, ref_template: str = pydantic.json_schema.DEFAULT_REF_TEMPLATE, schema_generator: type[pydantic.json_schema.GenerateJsonSchema] = pydantic.json_schema.GenerateJsonSchema, mode: pydantic.json_schema.JsonSchemaMode = "validation") -> dict[str, t.Any]:
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