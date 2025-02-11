import asyncio
import pathlib
import sys

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp import MCPToolkit

async def main(prompt: str) -> None:
    model = ChatGroq(model="llama-3.1-8b-instant")  # requires GROQ_API_KEY
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            toolkit = MCPToolkit(session=session)
            await toolkit.initialize()
            tools = toolkit.get_tools()
            tools_map = {tool.name: tool for tool in tools}
            tools_model = model.bind_tools(tools)
            messages = [HumanMessage(prompt)]
            messages.append(await tools_model.ainvoke(messages))
            for tool_call in messages[-1].tool_calls:
                selected_tool = tools_map[tool_call["name"].lower()]
                tool_msg = await selected_tool.ainvoke(tool_call)
                messages.append(tool_msg)
            result = await (tools_model | StrOutputParser()).ainvoke(messages)
            print(result)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))


In the provided code, I have made the following changes to follow the given rules:

1. Initialized the tools before accessing them by calling `await toolkit.initialize()` before getting the tools.
2. Managed tool state with a list by storing the tools in the `tools` variable and creating a `tools_map` dictionary to easily access tools by name.
3. Handled tools using the session object by passing the `session` object to the `MCPToolkit` constructor.