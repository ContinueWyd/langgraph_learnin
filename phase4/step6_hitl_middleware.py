import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    print(f"  [tool] get_weather({city})")
    return f"{city}：晴，25°C"

@tool
def delete_data(confirm: str) -> str:
    """删除所有测试数据。这是一个敏感操作。"""
    print(f"  [tool] delete_data(confirm={confirm})")
    return "所有测试数据已删除"

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

hitl = HumanInTheLoopMiddleware(
    interrupt_on={"delete_data": True},
)

agent = create_agent(
    model=llm,
    tools=[get_weather, delete_data],
    middleware=[hitl],
    checkpointer=InMemorySaver(),
    system_prompt="你是执行助手。用户明确要求调用工具时，直接调用，不要反问。",
)

config = {"configurable": {"thread_id": "hitl-mw-1"}}

print("===== 第一次 invoke：要求调 delete_data =====")
r1 = agent.invoke(
    {"messages": [("user", "请帮我删除所有测试数据")]},
    config,
)
print("  '__interrupt__':", r1.get("__interrupt__"))
print("  消息数:", len(r1["messages"]))

print("\n===== 第二次 invoke：人类批准 =====")
r2 = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config,
)
for m in r2["messages"]:
    print(f"  {type(m).__name__}: {m.content}")