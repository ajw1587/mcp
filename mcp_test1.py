from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP("Demo")

# 덧셈 기능을 제공하는 도구(Tool) 등록
@mcp.tool()
def add(a: int, b: int) -> int:
    """두 개의 숫자를 더하여 반환합니다."""
    return a + b

# 개인화된 인사말을 제공하는 리소스(resource) 등록
@mcp.resource("greeting://{name}")
def get_treeting(name: str) -> str:
    """이름이 들어간 인삿말을을 반환합니다."""
    return f"안녕하세요, {name}님!"


if __name__ == "__main__":
    print("test")
    mcp.run(transport="sse")