import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

summarizer = SummarizationMiddleware(
    model=llm,
    trigger=("tokens", 100),      # 超过 500 token 触发
    keep=("messages", 2),          # 保留最近 4 条
)

agent = create_agent(
    model=llm,
    tools=[],
    middleware=[summarizer],
    checkpointer=InMemorySaver(),   # ← 显式加
)

print("===== 连续多轮对话，观察消息数变化 =====")
config = {"configurable": {"thread_id": "summary-test-1"}}

print("===== 连续多轮对话，观察消息数变化 =====")
for i in range(1, 9):
    result = agent.invoke(
        {"messages": [HumanMessage(content=f"这是第 {i} 轮对话，请简单回复。")]},
        config,
    )
    n = len(result["messages"])
    print(f"\n第 {i} 轮 → 当前消息数: {n}")
    for j, m in enumerate(result["messages"]):
        # 每条消息只打印前 60 字符，避免刷屏
        content = m.content[:60].replace("\n", " ")
        print(f"    [{j}] {type(m).__name__}: {content}")