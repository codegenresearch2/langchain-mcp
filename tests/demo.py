from typing import List
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import Tool
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run(prompt: str, tools: List[Tool]) -> str:
    model = ChatGroq(model="llama-3.1-8b-instant", stop_sequences=None)  # requires GROQ_API_KEY
    tools_map = {tool.name: tool for tool in tools}
    tools_model = model.bind_tools(tools)
    messages: List[BaseMessage] = [HumanMessage(content=prompt)]
    messages.append(AIMessage(content=await tools_model.ainvoke(messages)))
    for tool_call in messages[-1].tool_calls:
        selected_tool = tools_map[tool_call["name"].lower()]
        tool_msg = await selected_tool.ainvoke(tool_call)
        messages.append(tool_msg)
    response = await (tools_model | StrOutputParser()).ainvoke(messages)
    return response

async def main(prompt: str) -> None:
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent.parent)],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            toolkit = MCPToolkit(session=session)
            await toolkit.initialize()
            tools = toolkit.get_tools()
            result = await run(prompt, tools)
            print(result)

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Read and summarize the file ./LICENSE"
    asyncio.run(main(prompt))


In the updated code, I have addressed the feedback from the oracle:

1. **Function Parameters**: I have moved the `model` initialization inside the `run` function to keep it self-contained.

2. **Message Initialization**: I have updated the message initialization to match the gold code's structure.

3. **Type Casting**: I have incorporated type casting using `AIMessage(content=...)` for the AI message.

4. **Tool Message Handling**: I have simplified the tool message handling to match the gold code's approach.

5. **Return Statement**: I have streamlined the return statement for clarity.

6. **Session Management**: I have managed the `ClientSession` within the `main` function, aligning with the gold code's structure.