from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage



'''
父图：
  START ──► parent_node ──► (subgraph) ──► fallback_node ──► END
                               │
                               │ (子图内部)
                               ▼
子图：
  START ──► child_node ──┬── (正常结束) return Command(goto=END) 
                         │      └─► 交还控制权，父图顺着边走到 fallback_node
                         │
                         └── (触发跳转) return Command(goto="fallback_node", graph=Command.PARENT)
                                └─► 直接跨图空降到父图的 fallback_node，无视父图原来的边                      
'''

class State(TypedDict):
    messages: list
    trigger_parent: bool


# ================= 子图节点 =================
# 注意：Literal 里只写 "__end__"，强制用 Command.PARENT 跳转不受静态检查限制
def child_node(state: State) -> Command[Literal["__end__"]]:
    print(f"  [child_node] 收到消息: {[m.content for m in state['messages']]}")

    if state.get("trigger_parent"):
        print("  [child_node] 检测到 trigger_parent=True，准备跨图跳转到父图的 fallback_node")
        return Command(
            goto="fallback_node",
            graph=Command.PARENT,
            update={"messages": [AIMessage(content="子图已执行完毕，跨图跳回父图", name="child_node")]}
        )

    print("  [child_node] 正常结束，返回父图")
    return Command(
        goto=END,
        update={"messages": [AIMessage(content="子图正常结束", name="child_node")]}
    )


# 构建并编译子图
child_graph = StateGraph(State)
child_graph.add_node("child_node", child_node)
child_graph.add_edge(START, "child_node")
child_compiled = child_graph.compile()


# ================= 父图节点 =================
def parent_node(state: State):
    print("  [parent_node] 开始执行")
    return {"messages": [AIMessage(content="父图节点已处理", name="parent_node")]}


def fallback_node(state: State):
    print("  [fallback_node] 执行收尾")
    return {"messages": [AIMessage(content="收尾节点执行完毕", name="fallback_node")]}


# 构建父图
parent_graph = StateGraph(State)
parent_graph.add_node("parent_node", parent_node)
parent_graph.add_node("subgraph", child_compiled)  # 必须传入编译后的子图
parent_graph.add_node("fallback_node", fallback_node)

parent_graph.add_edge(START, "parent_node")
parent_graph.add_edge("parent_node", "subgraph")
parent_graph.add_edge("subgraph", "fallback_node")
parent_graph.add_edge("fallback_node", END)

app = parent_graph.compile()

# ================= 测试 =================
print("===== 测试 1：正常流程 =====")
r1 = app.invoke({
    "messages": [HumanMessage(content="正常任务")],
    "trigger_parent": False
})
for m in r1["messages"]:
    print(f"    ({getattr(m, 'name', 'unknown')}) {m.content}")

print("\n===== 测试 2：触发跨图跳转 =====")
r2 = app.invoke({
    "messages": [HumanMessage(content="触发跨图任务")],
    "trigger_parent": True
})
for m in r2["messages"]:
    print(f"    ({getattr(m, 'name', 'unknown')}) {m.content}")