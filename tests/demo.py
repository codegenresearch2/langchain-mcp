import asyncio
import pathlib
import sys
import typing as t

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools.base import BaseTool
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp import MCPToolkit

async def run(tools: list[BaseTool], prompt: str) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant")  # requires GROQ_API_KEY
    tools_model = model.bind_tools(tools)
    tools_map = {tool.name: tool for tool in tools}
    messages = [HumanMessage(content=prompt)]
    messages.append(t.cast(BaseMessage, await tools_model.ainvoke(messages)))
    for tool_call in messages[-1].tool_calls:
        selected_tool = tools_map[tool_call["name"].lower()]
        tool_msg = await selected_tool.ainvoke(tool_call)
        messages.append(tool_msg)
    result = await (tools_model | StrOutputParser()).ainvoke(messages)
    return result

async def main(prompt: str) -> None:
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            toolkit = MCPToolkit(session=session)
            await toolkit.initialize()
            result = await run(toolkit.get_tools(), prompt)
            print(result)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))