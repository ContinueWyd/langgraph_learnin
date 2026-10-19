import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

# 1. 配置 PII 检测：检测手机号、邮箱
from langchain.agents.middleware import PIIMiddleware

# 邮箱：内置类型
pii_email = PIIMiddleware("email", strategy="redact", apply_to_input=True)

# 手机号：自定义正则（内置没有 phone_number）
pii_phone = PIIMiddleware(
    "phone",
    detector=r"1[3-9]\d{9}",   # 中国大陆手机号简单匹配
    strategy="redact",
    apply_to_input=True,
)

agent = create_agent(
    model=llm,
    tools=[],
    middleware=[pii_email, pii_phone],
    checkpointer=InMemorySaver(),
)
# 2. 加一个自定义工具，让模型可以主动查脱敏后的数据
# （这一步可选，先跑纯对话看看脱敏效果）
agent = create_agent(
    model=llm,
    tools=[],
    middleware=[pii_email, pii_phone],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "pii-test-1"}}

print("===== 第一次 invoke：含手机号 =====")
r1 = agent.invoke(
    {"messages": [("user", "我的手机号是 13812345678，帮我记一下。")]},
    config,
)
print("  模型回答:", r1["messages"][-1].content)
print("  历史消息数:", len(r1["messages"]))

print("\n===== 第二次 invoke：问刚才的号码 =====")
r2 = agent.invoke(
    {"messages": [("user", "我刚才告诉你的手机号是多少？")]},
    config,
)
print("  模型回答:", r2["messages"][-1].content)