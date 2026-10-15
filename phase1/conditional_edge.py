from typing import Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import HumanMessage, AIMessage

def router_node(state: MessagesState):
    last = state["messages"][-1].content
    print("router_node 收到:", last)
    return {}

def route_decision(state: MessagesState) -> Literal["greet", "farewell"]:
    last = state["messages"][-1].content
    if "你好" in last or "hello" in last.lower():
        return "greet"
    return "farewell"

def greet_node(state: MessagesState):
    return {"messages": [AIMessage(content="你好，我是 greet 分支")]}

def farewell_node(state: MessagesState):
    return {"messages": [AIMessage(content="再见，我是 farewell 分支")]}

g = StateGraph(MessagesState)
g.add_node("router", router_node)
g.add_node("greet", greet_node)
g.add_node("farewell", farewell_node)
g.add_edge(START, "router")
g.add_conditional_edges("router", route_decision)
g.add_edge("greet", END)
g.add_edge("farewell", END)

app = g.compile()

for user_input in ["你好", "拜拜"]:
    print(f"\n===== 输入: {user_input} =====")
    result = app.invoke({"messages": [HumanMessage(content=user_input)]})
    print("最终消息数:", len(result["messages"]))
    print("最后一条:", result["messages"][-1].content)