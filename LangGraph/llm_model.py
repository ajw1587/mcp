import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import config

from langchain_ollama import ChatOllama


# LLM 설정
llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0
)
