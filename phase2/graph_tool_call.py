import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

load_dotenv()

'''        START
          │
          ▼
     ┌─────────┐
     │  agent  │  ← llm_with_tools.invoke
     └────┬────┘
          │  ← should_continue
    ┌─────┴─────┐
    │有 tool_calls│   无 tool_calls
    ▼            ▼
┌────────┐      END
│ tools  │  ← ToolNode
└───┬────┘
    │
    └────────► 回到 agent（循环）

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

def agent_node(state: MessagesState):
    print("agent_node 收到", len(state["messages"]), "条消息")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState) -> str:
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return END

g = StateGraph(MessagesState)
g.add_node("agent", agent_node)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile()

result = app.invoke({"messages": [HumanMessage(content="北京今天天气怎么样？")]})
print("\n===== 最终对话 =====")
for m in result["messages"]:
    print(f"{type(m).__name__}: {getattr(m, 'content', '')}")