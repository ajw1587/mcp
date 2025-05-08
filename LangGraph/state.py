from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


"""
add_messages는 아래처럼 메시지가 순차적으로 쌓인다.

"messages": [
    {"role": "user", "content": "안녕?"},
    {"role": "assistant", "content": "안녕하세요!"}
]
"""
class State(TypedDict):
    messages: Annotated[list, add_messages]
    text2: Annotated[list, add_messages]