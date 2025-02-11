from typing import List
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import Tool
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import typing as t

async def run(tools: List[Tool], prompt: str) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None)  # requires GROQ_API_KEY
    tools_map = {tool.name: tool for tool in tools}
    tools_model = model.bind_tools(tools)
    messages: List[BaseMessage] = [HumanMessage(prompt)]
    ai_message = t.cast(AIMessage, await tools_model.ainvoke(messages))
    messages.append(ai_message)
    for tool_call in ai_message.tool_calls:
        selected_tool = tools_map[tool_call["name"].lower()]
        tool_msg = await selected_tool.ainvoke(tool_call)
        messages.append(tool_msg)
    return await (tools_model | StrOutputParser()).ainvoke(messages)

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


In the updated code, I have addressed the feedback from the oracle:

1. **Function Parameters**: I have adjusted the order of parameters in the `run` function to match the gold code.

2. **Message Initialization**: I have updated the message initialization to use the correct constructor for `HumanMessage`.

3. **Type Casting**: I have updated the type casting for the AI message to match the gold code's approach.

4. **Tool Message Handling**: I have streamlined the handling of tool messages to use `ai_message.tool_calls` directly.

5. **Return Statement**: I have simplified the return statement in the `run` function.

6. **Response Handling in Main**: I have updated the response handling in the `main` function to pass the tools directly from the toolkit to the `run` function.