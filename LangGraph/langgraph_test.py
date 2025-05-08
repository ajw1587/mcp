import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import config
from LangGraph.state import State

# Graph 정의
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.client import MultiServerMCPClient

from LangGraph.llm_model import llm
from LangGraph.tools import web_search_tool, mcp_tool_config, hello_tool, calculate_tool, summarize, default_response
from LangGraph.route_tools import route_from_first_chatbot, route_from_second_chatbot


async def main():
    async with MultiServerMCPClient(mcp_tool_config) as client:
        # Search Tool 정의
        mcp_all_tools = client.get_tools()
        cmd_tool = [t for t in mcp_all_tools if t.name=="execute_command"]
        first_tools = [hello_tool, web_search_tool]
        second_tools = cmd_tool + [calculate_tool]

        # Tool을 LLM이 사용할 수 있도록 셋팅팅
        llm_with_tools_first = llm.bind_tools(first_tools)
        llm_with_tools_second = llm.bind_tools(second_tools)

        # ChatBot 선언
        def first_chatbot(state: State):
            return {"messages": [llm_with_tools_first.invoke(state["messages"])]}
        
        def second_chatbot(state: State):
            return {"messages": [llm_with_tools_second.invoke(state["messages"])]}

        #================================================================#
        # Graph Builder 선언
        graph_builder = StateGraph(State)

        # Node 선언
        cmd_node = ToolNode(tools=cmd_tool)
        hello_node = ToolNode(tools=[hello_tool])
        cal_node = ToolNode(tools=[calculate_tool])
        search_node = ToolNode(tools=[web_search_tool])

        # Node 추가
        graph_builder.add_node("first_chatbot", first_chatbot)
        graph_builder.add_node("second_chatbot", second_chatbot)
        graph_builder.add_node("hello_tool", hello_node)
        graph_builder.add_node("search_tool", search_node)
        graph_builder.add_node("cal_tool", cal_node)
        graph_builder.add_node("cmd_tool", cmd_node)
        graph_builder.add_node("summarize", summarize)
        graph_builder.add_node("default_tool", default_response)

        # Edge 연결
        graph_builder.add_edge(START, "first_chatbot")
        graph_builder.add_conditional_edges(
            "first_chatbot",
            route_from_first_chatbot,
            {
                "hello_tool": "hello_tool",
                "search_tool": "search_tool",
                "default_tool": "default_tool"
            }
        )
        graph_builder.add_edge("hello_tool", "second_chatbot")
        graph_builder.add_conditional_edges(
            "second_chatbot",
            route_from_second_chatbot,
            {
                "cal_tool": "cal_tool",
                "cmd_tool": "cmd_tool",
                "default_tool": "default_tool"
            }
        )
        graph_builder.add_edge("cal_tool", "summarize")
        graph_builder.add_edge("cmd_tool", "summarize")

        graph_builder.add_edge("summarize", END)
        graph_builder.add_edge("search_tool", END)
        graph_builder.add_edge("default_tool", END)


        graph = graph_builder.compile()
        # 그래프 그리기
        from IPython.display import Image, display
        try:
            display(
                Image(
                    graph.get_graph().draw_mermaid_png(
                        output_file_path="./chatbot_with_tool.png"
                    )
                )
            )
        except Exception:
            pass

        initial_state = {
            "messages": [
                {"role": "user", "content": "안녕하세요. pwd."}
            ],
            "text": [
                {"role": "user", "content": "this is text"}
            ]
        }
        result = await graph.ainvoke(initial_state)
        print(result)

import asyncio

asyncio.run(main())
