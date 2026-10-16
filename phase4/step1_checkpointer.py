from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage

def echo_node(state: MessagesState):
    last = state["messages"][-1].content
    print(f"  [echo_node] 收到 {len(state['messages'])} 条消息，最后一条: {last}")
    return {"messages": [AIMessage(content=f"你说的是：{last}")]}

g = StateGraph(MessagesState)
g.add_node("echo", echo_node)
g.add_edge(START, "echo")
g.add_edge("echo", END)

# 关键：传入 checkpointer
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    app = g.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "user-1"}}

    print("===== 第一轮 =====")
    r1 = app.invoke({"messages": [HumanMessage(content="我叫小明")]}, config)
    print(f"  最终消息数: {len(r1['messages'])}")

    print("\n===== 第二轮（同一 thread_id） =====")
    r2 = app.invoke({"messages": [HumanMessage(content="我叫什么？")]}, config)
    print(f"  最终消息数: {len(r2['messages'])}")
    print("  完整对话:")
    for m in r2["messages"]:
        print(f"    {type(m).__name__}: {m.content}")

    print("\n===== 第三轮（不同 thread_id） =====")
    config2 = {"configurable": {"thread_id": "user-2"}}
    r3 = app.invoke({"messages": [HumanMessage(content="我叫什么？")]}, config2)
    print(f"  最终消息数: {len(r3['messages'])}")