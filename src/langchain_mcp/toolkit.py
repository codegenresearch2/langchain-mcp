# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

import asyncio
import warnings
from collections.abc import Callable

import pydantic
import pydantic_core
import typing_extensions as t
from langchain_core.tools.base import BaseTool, BaseToolkit, ToolException
from mcp import ClientSession


class MCPToolkit(BaseToolkit):
    """
    MCP server toolkit
    """

    session: ClientSession
    _tools: list[BaseTool] = []
    _initialized: bool = False

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    async def initialize(self):
        if not self._initialized:
            self._tools = [
                MCPTool(
                    toolkit=self,
                    name=tool.name,
                    description=tool.description or "",
                    args_schema=create_schema_model(tool.inputSchema),
                )
                for tool in (await self.session.list_tools()).tools
            ]
            self._initialized = True
        return None

    @t.override
    async def get_tools(self) -> list[BaseTool]:  # type: ignore[override]
        if not self._initialized:
            raise RuntimeError("MCPToolkit has not been initialized. Call initialize() first.")
        return self._tools


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
    session: ClientSession
    handle_tool_error: bool | str | Callable[[ToolException], str] | None = True

    @t.override
    def _run(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        warnings.warn(
            "Invoke this tool asynchronously using `ainvoke`. This method exists only to satisfy tests.", stacklevel=1
        )
        return asyncio.run(self._arun(*args, **kwargs))

    @t.override
    async def _arun(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        result = await self.session.call_tool(self.name, arguments=kwargs)
        content = pydantic_core.to_json(result.content).decode()
        if result.isError:
            raise ToolException(content)
        return content

    @t.override
    @property
    def tool_call_schema(self) -> type[pydantic.BaseModel]:
        assert self.args_schema is not None  # noqa: S101
        return self.args_schema


### Explanation of Changes:
1. **Initialization Logic**: Added an instance variable `_tools` to store the fetched tools and initialized it as an empty list. The `initialize` method now sets this list and marks the toolkit as initialized.

2. **Error Handling**: Added a `RuntimeError` to be raised if `get_tools` is called before `initialize`.

3. **Method Signatures**: Ensured that `initialize` returns `None` and `get_tools` returns a list of `BaseTool`.

4. **Class Attributes**: Renamed `_initialized` to `_tools` and added a new `_initialized` attribute to track initialization status.

5. **Schema Model Creation**: Adjusted the `create_schema_model` function to match the expected parameters for `model_json_schema`.

6. **Session Parameter**: Added the `session` attribute to the `MCPTool` class.

7. **Warning Message**: Updated the warning message in `_run` to be more descriptive.