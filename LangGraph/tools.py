import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import config
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from LangGraph.state import State


web_search_tool = TavilySearchResults(tavily_api_key=config.TAVILY_API_KEY, max_results=2)

mcp_tool_config = {
        "desktop-commander": {
            "command": "npx",
            "args": ["-y", "@smithery/cli@latest", "run", "@wonderwhy-er/desktop-commander", "--key", "c430d65f-3d79-46ce-a542-ff4a48195bab"],
            "transport": "stdio"
        }
    }

@tool
async def hello_tool(text: str) -> str:
    """
    Organize the user's greeting.
    """
    return f"hello_tool 실행 - {text}"

@tool
async def calculate_tool(text: str) -> str:
    """
    문장에 더하기(+) 표시가 있으면 실행됩니다.
    """
    try:
        result = eval(text, {"__builtins__": {}})
        return f"결과: {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"

def summarize(state: State):
    return {"messages": state["messages"] + [{"role": "system", "content": "MCP 실행 완료"}]}

def default_response(state: State):
    return {"messages": state["messages"] + [{"role": "system", "content": "적절한 툴을 판단하지 못했습니다."}]}
