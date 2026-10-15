import os
from typing import Literal
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

load_dotenv()


'''                    START
                      │
                      ▼
              ┌───────────────┐
              │     agent     │
              │               │
              │  1. 调模型     │
              │  2. 有         │
              │  tool_calls?  │
              └───────┬───────┘
                      │
          ┌───────────┴───────────┐
          │                       │
   Command(goto="tools")   Command(goto=END)
   update={"messages":[response]}  update={"messages":[response]}
          │                       │
          ▼                       ▼
    ┌──────────┐                 END
    │  tools   │
    │ ToolNode │
    └────┬─────┘
         │
         │  回边
         └──────────► 回到 agent
'''


@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    fake_db = {"北京": "晴，25°C", "上海": "小雨，22°C"}
    result = fake_db.get(city, f"{city}：暂无数据")
    print(f"[tool] get_weather(city={city}) -> {result}")
    return result

llm = init_chat_model(
    model=os.getenv("MODEL_NAME"),
    model_provider="openai",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: MessagesState) -> Command[Literal["tools", "__end__"]]:
    print("agent_node 收到", len(state["messages"]), "条消息")
    response = llm_with_tools.invoke(state["messages"])
    if response.tool_calls:
        return Command(goto="tools", update={"messages": [response]})
    return Command(goto=END, update={"messages": [response]})

g = StateGraph(MessagesState)
g.add_node("agent", agent_node)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_edge("tools", "agent")

app = g.compile()

result = app.invoke({"messages": [HumanMessage(content="北京今天天气怎么样？")]})
print("\n===== 最终对话 =====")
for m in result["messages"]:
    print(f"{type(m).__name__}: {getattr(m, 'content', '')}")