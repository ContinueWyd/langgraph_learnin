from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import HumanMessage, AIMessage

def node_1(state: MessagesState):
    print("node_1 收到:", state["messages"])
    return {"messages": [AIMessage(content="node_1 说的话")]}

def node_2(state: MessagesState):
    print("node_2 收到:", state["messages"])
    return {"messages": [AIMessage(content="node_2 说的话")]}

g = StateGraph(MessagesState)
g.add_node("n1", node_1)
g.add_node("n2", node_2)
g.add_edge(START, "n1")
g.add_edge("n1", "n2")
g.add_edge("n2", END)

app = g.compile()
result = app.invoke({"messages": [HumanMessage(content="用户输入")]})
print("最终结果:")
for m in result["messages"]:
    print(" ", type(m).__name__, "->", m.content)