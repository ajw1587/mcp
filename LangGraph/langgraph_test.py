from langchain_ollama import OllamaLLM

# Ollama 모델 연결 (예: llama3 사용)
llm = OllamaLLM(
    model="qwen2.5:0.5b",
    temperature=0,
)

# Ollama 모델에게 전달할 프롬프트 구성
prompt = f"안녕하세요"

response = llm.invoke(prompt)
print(response)