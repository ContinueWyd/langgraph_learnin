import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    return f"{city}：晴，25°C"

llm = init_chat_model(
    model=os.getenv("MODEL_NAME"),
    model_provider="openai",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: MessagesState) -> str:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

g = StateGraph(MessagesState)
g.add_node("agent", agent_node)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile()

print("===== 开始执行 =====")
result = app.invoke({"messages": [HumanMessage(content="北京今天天气怎么样？")]})
print("最终回答:", result["messages"][-1].content)
