# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: MIT

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "langchain-mcp",
#     "langchain-groq",
# ]
# ///

import asyncio
import pathlib
import sys
from typing import List

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp import MCPToolkit

class ToolManager:
    def __init__(self):
        self.toolkit = None
        self.tools = None
        self.tools_map = None

    async def initialize_toolkit(self, session):
        self.toolkit = MCPToolkit(session=session)
        await self.initialize()

    async def initialize(self):
        if self.toolkit is None:
            raise ValueError("Toolkit is not initialized. Call initialize_toolkit first.")
        self.tools = await self.toolkit.get_tools()
        self.tools_map = {tool.name: tool for tool in self.tools}

async def run(tools: List[Tool], prompt: str) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant")  # requires GROQ_API_KEY
    tools_model = model.bind_tools(tools)
    messages = [HumanMessage(prompt)]
    messages.append(await tools_model.ainvoke(messages))
    for tool_call in messages[-1].tool_calls:
        selected_tool = tools_model.tools_map[tool_call["name"].lower()]
        tool_msg = await selected_tool.ainvoke(tool_call)
        messages.append(AIMessage(content=tool_msg.content))
    result = await (tools_model | StrOutputParser()).ainvoke(messages)
    return result

async def main(prompt: str) -> None:
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            tool_manager = ToolManager()
            await tool_manager.initialize_toolkit(session)
            result = await run(tool_manager.tools, prompt)
            print(result)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))