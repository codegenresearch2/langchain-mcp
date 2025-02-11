import asyncio
import pathlib
import sys
from typing import List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import AIMessage
from typing import cast

from langchain_mcp import MCPToolkit

async def run(tools: List[BaseTool], prompt: str) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None)  # requires GROQ_API_KEY
    tools_map = {tool.name: tool for tool in tools}
    tools_model = model.bind_tools(tools)
    messages: List[BaseMessage] = [HumanMessage(content=prompt)]
    ai_message = cast(AIMessage, await tools_model.ainvoke(messages))
    messages.append(ai_message)

    for tool_call in ai_message.tool_calls:
        selected_tool = tools_map[tool_call.name]
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
            response = await run(toolkit.get_tools(), prompt)
            print(response)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))


In the revised code, I have addressed the feedback by using the correct type annotations, casting the result of `tools_model.ainvoke` to `AIMessage`, passing the correct arguments when invoking the tool, using consistent variable naming, simplifying the return statement, and passing the tools directly from `toolkit.get_tools()`.