from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated, TypedDict
from operator import add
from langgraph.channels.untracked_value import UntrackedValue

class State(TypedDict):
    messages: Annotated[list, add]
    temp_cache: UntrackedValue[list]   # 不持久化

def node_a(state: State):
    print(f"  [node_a] temp_cache 当前值: {state.get('temp_cache')}")
    # 模拟赋值
    new_cache = (state.get("temp_cache") or []) + ["node_a 写入"]
    return {"messages": ["node_a 跑了"], "temp_cache": new_cache}

def node_b(state: State):
    print(f"  [node_b] temp_cache 当前值: {state.get('temp_cache')}")
    return {"messages": ["node_b 跑了"]}

g = StateGraph(State)
g.add_node("a", node_a)
g.add_node("b", node_b)
g.add_edge(START, "a")
g.add_edge("a", "b")
g.add_edge("b", END)

with SqliteSaver.from_conn_string("untracked.db") as checkpointer:
    app = g.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "untracked-1"}}

    print("===== 第一次 invoke =====")
    r1 = app.invoke({"messages": [], "temp_cache": [""]}, config)
    print("  最终 temp_cache:", r1.get("temp_cache"))

    print("\n===== 第二次 invoke（同 thread_id） =====")
    r2 = app.invoke({"messages": [], "temp_cache": [""]}, config)
    print("  最终 temp_cache:", r2.get("temp_cache"))