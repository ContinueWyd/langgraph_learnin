from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: Annotated[list, add]

def node_1(state: State):
    return {"messages": ["node_1 说的话"]}

def clear_node(state: State):
    print("clear_node 收到:", state["messages"])
    return {"messages": []}

def node_2(state: State):
    print("node_2 收到:", state["messages"])
    return {"messages": ["node_2 说的话"]}

g = StateGraph(State)
g.add_node("n1", node_1)
g.add_node("clear", clear_node)
g.add_node("n2", node_2)
g.add_edge(START, "n1")
g.add_edge("n1", "clear")
g.add_edge("clear", "n2")
g.add_edge("n2", END)

app = g.compile()
result = app.invoke({"messages": ["用户输入"]})
print("最终结果:", result)