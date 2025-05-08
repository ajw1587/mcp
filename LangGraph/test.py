from typing import Annotated
from typing_extensions import TypedDict
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_mcp_adapters.client import MultiServerMCPClient

# 상태 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]

memory = MemorySaver()

# 사용자 정의 툴
@tool
async def hello_tool(text: str) -> str:
    return f"hello_tool 실행 - {text}"

@tool
async def calculate_tool(text: str) -> str:
    try:
        result = eval(text, {"__builtins__": {}})
        return f"결과: {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"

# 메인 실행 함수
async def main():
    server_config = {
        "desktop-commander": {
            "command": "npx",
            "args": ["-y", "@smithery/cli@latest", "run", "@wonderwhy-er/desktop-commander", "--key", "c430d65f-3d79-46ce-a542-ff4a48195bab"],
            "transport": "stdio"
        }
    }

    # Web search 툴
    web_search_tool = TavilySearchResults(tavily_api_key="your_tavily_key", max_results=2)

    async with MultiServerMCPClient(server_config) as client:
        mcp_tools = client.get_tools()
        all_tools = [hello_tool, calculate_tool, web_search_tool] + mcp_tools
        llm = ChatOpenAI(model="gpt-4").bind_tools(all_tools)

        # 노드 정의
        def chatbot(state: State):
            return {"messages": [llm.invoke(state["messages"])]}

        mcp_node = ToolNode(tools=mcp_tools)
        hello_node = ToolNode(tools=[hello_tool])
        calc_node = ToolNode(tools=[calculate_tool])
        search_node = ToolNode(tools=[web_search_tool])

        def summarize(state: State):
            return {"messages": state["messages"] + [{"role": "system", "content": "MCP 실행 완료"}]}

        def default_response(state: State):
            return {"messages": state["messages"] + [{"role": "system", "content": "적절한 툴을 판단하지 못했습니다."}]}

        # chatbot 분기: MCP 또는 hello_tool 또는 fallback
        def route_from_chatbot(state: State) -> str:
            msg = state["messages"][-1]
            tool_calls = msg.get("additional_kwargs", {}).get("tool_calls", [])
            if not tool_calls:
                return "default_response"
            name = tool_calls[0]["function"]["name"]
            if "desktop" in name or "execute_command" in name:
                return "mcp"
            elif "hello_tool" in name:
                return "hello"
            return "default_response"

        # hello 실행 후 분기: calc or search
        def route_from_hello(state: State) -> str:
            msg = state["messages"][-1]
            tool_calls = msg.get("additional_kwargs", {}).get("tool_calls", [])
            if not tool_calls:
                return "default_response"
            name = tool_calls[0]["function"]["name"]
            if "calculate_tool" in name:
                return "calc"
            elif "tavily" in name:
                return "search"
            return "default_response"

        # LangGraph 구성
        builder = StateGraph(State)
        builder.add_node("chatbot", chatbot)
        builder.add_node("mcp", mcp_node)
        builder.add_node("hello", hello_node)
        builder.add_node("calc", calc_node)
        builder.add_node("search", search_node)
        builder.add_node("summarize", summarize)
        builder.add_node("default_response", default_response)

        builder.add_conditional_edges("chatbot", route_from_chatbot, {
            "mcp": "mcp",
            "hello": "hello",
            "default_response": "default_response"
        })
        builder.add_conditional_edges("hello", route_from_hello, {
            "calc": "calc",
            "search": "search",
            "default_response": "default_response"
        })

        builder.add_edge("mcp", "summarize")
        builder.add_edge("calc", END)
        builder.add_edge("search", END)
        builder.add_edge("summarize", END)
        builder.add_edge("default_response", END)

        builder.set_entry_point("chatbot")
        app = builder.compile().configure(checkpointer=memory)

        # 테스트 실행
        result = app.invoke({
            "messages": [{"role": "user", "content": "2 + 3 * 4는 얼마야?"}]
        })
        print("🟢 실행 결과:\n", result)

await main()
