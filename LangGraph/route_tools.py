from langgraph.graph import END
from LangGraph.state import State


# chatbot route
def route_from_first_chatbot(state: State) -> str:
    msg = state["messages"][-1]
    tool_calls = msg.tool_calls

    if not tool_calls:
        return "default_tool"
    
    name = tool_calls[-1]["name"]
    if "tavily_search_results_json" in name:
        return "search_tool"
    elif "hello_tool" in name:
        return "hello_tool"
    return "default_tool"

# hello route
def route_from_second_chatbot(state: State) -> str:
    msg = state["messages"][-1]
    tool_calls = msg.tool_calls

    if not tool_calls:
        return "default_tool"
    
    name = tool_calls[-1]["name"]
    if "cal_tool" in name:
        return "cal_tool"
    elif "cmd_tool" in name:
        return "cmd_tool"
    return "default_tool"