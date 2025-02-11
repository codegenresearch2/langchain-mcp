# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

import asyncio
import warnings
from collections.abc import Callable
from typing import Any, List, Type

import pydantic
import pydantic_core
import typing_extensions as t
from langchain_core.tools.base import BaseTool, BaseToolkit, ToolException
from mcp import ClientSession, ListToolsResult, Tool
from pydantic import BaseModel

class MCPToolkit(BaseToolkit):
    """
    MCP server toolkit
    """

    session: ClientSession
    """The MCP session used to obtain the tools"""

    _initialized: bool = False

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    async def initialize(self) -> None:
        """Asynchronously initialize the MCP session."""
        if not self._initialized:
            await self.session.initialize()
            self._initialized = True

    @t.override
    async def get_tools(self) -> List[BaseTool]:
        """Asynchronously retrieve the tools from the MCP session."""
        if not self._initialized:
            await self.initialize()

        tools_result: ListToolsResult = await self.session.list_tools()
        return [
            MCPTool(
                toolkit=self,
                name=tool.name,
                description=tool.description or "",
                args_schema=create_schema_model(tool.inputSchema),
            )
            for tool in tools_result.tools
        ]

def create_schema_model(schema: dict[str, Any]) -> Type[BaseModel]:
    """Create a new model class that returns our JSON schema."""
    class Schema(BaseModel):
        model_config = pydantic.ConfigDict(extra="allow", arbitrary_types_allowed=True)

        @classmethod
        def model_json_schema(
            cls,
            by_alias: bool = True,
            ref_template: str = pydantic.json_schema.DEFAULT_REF_TEMPLATE,
            schema_generator: type[pydantic.json_schema.GenerateJsonSchema] = pydantic.json_schema.GenerateJsonSchema,
            mode: pydantic.json_schema.JsonSchemaMode = "validation",
        ) -> dict[str, Any]:
            return schema

    return Schema

class MCPTool(BaseTool):
    """
    MCP server tool
    """

    toolkit: MCPToolkit
    handle_tool_error: bool | str | Callable[[ToolException], str] | None = True

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Asynchronously run the MCP tool."""
        result = await self.toolkit.session.call_tool(self.name, arguments=kwargs)
        content = pydantic_core.to_json(result.content).decode()
        if result.isError:
            raise ToolException(content)
        return content

    @property
    def tool_call_schema(self) -> Type[BaseModel]:
        """Return the tool call schema."""
        assert self.args_schema is not None  # noqa: S101
        return self.args_schema