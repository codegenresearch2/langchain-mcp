// Copyright (C) 2024 Andrew Wason
// SPDX-License-Identifier: MIT

// /// script
// requires-python = ">=3.10"
// dependencies = [
//     "langchain-mcp",
//     "langchain-groq",
// ]
// ///

import asyncio
import pathlib
import sys

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp import MCPToolkit


async def run(prompt: str, tools: list[BaseTool]) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None)  // requires GROQ_API_KEY
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            toolkit = MCPToolkit(session=session)
            await toolkit.initialize()
            tools_map = {tool.name: tool for tool in tools}
            tools_model = model.bind_tools(tools)
            messages = [HumanMessage(content=prompt)]
            ai_message = await tools_model.ainvoke(messages)
            messages.append(t.cast(AIMessage, ai_message))
            for tool_call in ai_message.tool_calls:
                selected_tool = tools_map[tool_call["name"].lower()]
                tool_msg = await selected_tool.ainvoke(tool_call)
                messages.append(tool_msg)
            result = await (tools_model | StrOutputParser()).ainvoke(messages)
            return result


async def main(prompt: str, tools: list[BaseTool]) -> None:
    response = await run(prompt, tools)
    print(response)


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt, []))  // Assuming tools are initialized elsewhere