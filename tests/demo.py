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
import typing as t

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp import MCPToolkit, Tool


async def run(tools: list[BaseTool], model: ChatGroq, prompt: str) -> str:
    tools_map = {tool.name: tool for tool in tools}
    messages: list[BaseMessage] = [HumanMessage(content=prompt)]
    ai_message = await t.cast(AIMessage, model.ainvoke([messages[0]]))
    messages.append(ai_message)
    for tool_call in ai_message.tool_calls:
        selected_tool = tools_map[tool_call["name"].lower()]
        tool_msg = await selected_tool.ainvoke(tool_call)
        messages.append(tool_msg)
    result = await (model | StrOutputParser()).ainvoke(messages)
    return result


async def main(prompt: str) -> None:
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None)  # requires GROQ_API_KEY
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            toolkit = MCPToolkit(session=session)
            await toolkit.initialize()  # Initialize the toolkit before use
            response = await run(await toolkit.get_tools(), model, prompt)
            print(response)


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))