# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

import asyncio
import warnings
from collections.abc import Callable
from typing import List, Type

import pydantic
import pydantic_core
import typing_extensions as t
from langchain_core.tools.base import BaseTool, BaseToolkit, ToolException
from mcp import ClientSession

class MCPToolkit(BaseToolkit):
    """MCP server toolkit"""

    session: ClientSession
    """The MCP session used to obtain the tools"""

    _initialized: bool = False

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    async def initialize(self) -> None:
        """Initialize the toolkit"""
        if not self._initialized:
            await self.session.initialize()
            self._initialized = True

    @t.override
    async def get_tools(self) -> List[BaseTool]:
        """Get the tools from the toolkit"""
        if not self._initialized:
            await self.initialize()

        tools = []
        for tool in (await self.session.list_tools()).tools:
            tools.append(
                MCPTool(
                    toolkit=self,
                    name=tool.name,
                    description=tool.description or "",
                    args_schema=create_schema_model(tool.inputSchema),
                )
            )
        return tools

def create_schema_model(schema: dict[str, t.Any]) -> Type[pydantic.BaseModel]:
    """Create a new model class that returns our JSON schema"""
    class Schema(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="allow", arbitrary_types_allowed=True)

        @t.override
        @classmethod
        def model_json_schema(
            cls,
            by_alias: bool = True,
            ref_template: str = pydantic.json_schema.DEFAULT_REF_TEMPLATE,
            schema_generator: type[pydantic.json_schema.GenerateJsonSchema] = pydantic.json_schema.GenerateJsonSchema,
            mode: pydantic.json_schema.JsonSchemaMode = "validation",
        ) -> dict[str, t.Any]:
            return schema

    return Schema

class MCPTool(BaseTool):
    """MCP server tool"""

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
    def tool_call_schema(self) -> Type[pydantic.BaseModel]:
        assert self.args_schema is not None
        return self.args_schema

The code snippet has been rewritten to follow the provided rules. The `MCPToolkit` class now has a separate `initialize` method that can be called to initialize the toolkit. This change ensures that the toolkit is initialized before it is used. The code has also been modularized for better readability, and type hints have been added for clarity.