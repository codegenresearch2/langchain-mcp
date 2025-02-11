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

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp import MCPToolkit


async def run(tools, prompt, session):
    toolkit = MCPToolkit(session=session)
    await toolkit.initialize()
    tools_map = {tool.name: tool for tool in tools}
    messages = [HumanMessage(content=prompt)]
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None)
    ai_message = await model.ainvoke([messages[0]])
    messages.append(ai_message)
    for tool_call in ai_message.tool_calls:
        selected_tool = tools_map[tool_call["name"].lower()]
        tool_message = await selected_tool.ainvoke(tool_call["arguments"])
        messages.append(tool_message)
    result = await (model | StrOutputParser()).ainvoke(messages)
    return result


async def main(prompt):
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            toolkit = MCPToolkit(session=session)
            tools = await toolkit.get_tools()
            result = await run(tools, prompt, session)
            print(result)


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))