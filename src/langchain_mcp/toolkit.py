import asyncio
import warnings
from collections.abc import Callable
from typing import List, Any, Union, Type, Optional

import pydantic
import pydantic_core
import typing_extensions as t
from langchain_core.tools.base import BaseTool, BaseToolkit, ToolException
from mcp import ClientSession

class MCPToolkit(BaseToolkit):
    """\n    MCP server toolkit\n    """
    session: ClientSession
    """The MCP session used to obtain the tools"""

    _initialized: bool = False

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    async def initialize(self) -> None:
        if not self._initialized:
            await self.session.initialize()
            self._initialized = True

    async def get_tools(self) -> List[BaseTool]:
        await self.initialize()

        return [
            MCPTool(
                toolkit=self,
                name=tool.name,
                description=tool.description or "",
                args_schema=create_schema_model(tool.inputSchema),
            )
            for tool in (await self.session.list_tools()).tools
        ]

def create_schema_model(schema: dict[str, t.Any]) -> Type[pydantic.BaseModel]:
    class Schema(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="allow", arbitrary_types_allowed=True)

        @classmethod
        def model_json_schema(
            cls,
            by_alias: bool = True,
            ref_template: str = pydantic.json_schema.DEFAULT_REF_TEMPLATE,
            schema_generator: Type[pydantic.json_schema.GenerateJsonSchema] = pydantic.json_schema.GenerateJsonSchema,
            mode: pydantic.json_schema.JsonSchemaMode = "validation",
        ) -> dict[str, t.Any]:
            return schema

    return Schema

class MCPTool(BaseTool):
    """\n    MCP server tool\n    """
    toolkit: MCPToolkit
    handle_tool_error: Optional[Union[bool, str, Callable[[ToolException], str]]] = True

    async def _arun(self, *args: t.Any, **kwargs: t.Any) -> Any:
        result = await self.toolkit.session.call_tool(self.name, arguments=kwargs)
        content = pydantic_core.to_json(result.content).decode()
        if result.isError:
            raise ToolException(content)
        return content

    @property
    def tool_call_schema(self) -> Type[pydantic.BaseModel]:
        assert self.args_schema is not None  # noqa: S101
        return self.args_schema

The provided code snippet has been rewritten following the given rules. The changes include moving the initialization logic to a separate asynchronous method, improving type hinting for better clarity, and removing the synchronous `_run` method as it is not necessary for asynchronous operations.