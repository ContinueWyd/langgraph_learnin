from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: list

def node_1(state: State):
    print("node_1 收到:", state["messages"])
    return {"messages": ["node_1 说的话"]}

def node_2(state: State):
    print("node_2 收到:", state["messages"])
    return {"messages": ["node_2 说的话"]}

g = StateGraph(State)
g.add_node("n1", node_1)
g.add_node("n2", node_2)
g.add_edge(START, "n1")
g.add_edge("n1", "n2")
g.add_edge("n2", END)

app = g.compile()
result = app.invoke({"messages": ["用户输入"]})
print("最终结果:", result)