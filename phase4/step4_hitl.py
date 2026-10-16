from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command
from langchain_core.messages import AIMessage, HumanMessage

def step1_node(state: MessagesState):
    print("  [step1] 准备数据")
    return {"messages": [AIMessage(content="已准备好数据")]}

def approval_node(state: MessagesState):
    print("  [approval] 即将执行敏感操作，等待人类确认")
    decision = interrupt({
        "question": "是否批准执行删除操作？",
        "details": state["messages"][-1].content,
    })
    print(f"  [approval] 人类回复: {decision}")
    if decision == "yes":
        return {"messages": [AIMessage(content="操作已批准，执行中")]}
    return {"messages": [AIMessage(content="操作被拒绝")]}

def step3_node(state: MessagesState):
    print("  [step3] 结束")
    return {"messages": [AIMessage(content="流程结束")]}

g = StateGraph(MessagesState)
g.add_node("step1", step1_node)
g.add_node("approval", approval_node)
g.add_node("step3", step3_node)
g.add_edge(START, "step1")
g.add_edge("step1", "approval")
g.add_edge("approval", "step3")
g.add_edge("step3", END)

with SqliteSaver.from_conn_string("hitl.db") as checkpointer:
    app = g.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "approval-1"}}

    print("===== 第一次 invoke：跑到 interrupt 暂停 =====")
    r1 = app.invoke({"messages": [HumanMessage(content="请删除所有测试数据")]}, config)
    print("  返回:", r1)

    print("\n===== 第二次 invoke：人类回复 'yes' 恢复执行 =====")
    r2 = app.invoke(Command(resume="yes"), config)
    print("  最终消息:")
    for m in r2["messages"]:
        print(f"    {type(m).__name__}: {m.content}")