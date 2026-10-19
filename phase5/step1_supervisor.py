import os
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)


# ========== 子 Agent 1：数学计算 ==========
def math_worker(state: MessagesState):
    print("  [math_worker] 收到任务")
    prompt = [
        SystemMessage("你是一个数学专家，请直接计算结果，不要废话。"),
        state["messages"][-1]
    ]
    res = llm.invoke(prompt)
    print(f"  [math_worker] 返回: {res.content}")
    return {"messages": [AIMessage(content=f"[数学专家] {res.content}", name="math_worker")]}


# ========== 子 Agent 2：文本翻译 ==========
def text_worker(state: MessagesState):
    print("  [text_worker] 收到任务")
    prompt = [
        SystemMessage("你是一个翻译专家，请把内容翻译成英文，不要废话。"),
        state["messages"][-1]
    ]
    res = llm.invoke(prompt)
    print(f"  [text_worker] 返回: {res.content}")
    return {"messages": [AIMessage(content=f"[翻译专家] {res.content}", name="text_worker")]}


# ========== 主控 Agent：Supervisor ==========
def supervisor(state: MessagesState) -> Command[Literal["math_worker", "text_worker", "__end__"]]:
    print("  [supervisor] 正在决策...")
    system_prompt = SystemMessage(
        "你是一个任务调度员。根据用户请求，决定把任务派给谁：\n"
        "- 如果是数学题，回复 'math'\n"
        "- 如果是翻译，回复 'text'\n"
        "- 如果任务已经完成（看历史里是否已有 [数学专家] 或 [翻译专家] 的回答），回复 'done'\n"
        "只输出 math、text 或 done，不要输出其他任何字。"
    )

    # 把当前状态发给模型做判断
    res = llm.invoke([system_prompt] + state["messages"])
    decision = res.content.strip().lower()
    print(f"  [supervisor] 决定去: {decision}")

    if decision == "math":
        return Command(goto="math_worker")
    elif decision == "text":
        return Command(goto="text_worker")
    else:
        return Command(goto=END)


# ========== 搭图 ==========
g = StateGraph(MessagesState)
g.add_node("supervisor", supervisor)
g.add_node("math_worker", math_worker)
g.add_node("text_worker", text_worker)

g.add_edge(START, "supervisor")
g.add_edge("math_worker", "supervisor")
g.add_edge("text_worker", "supervisor")

app = g.compile()

# ========== 测试 1：数学题 ==========
print("===== 测试 1：数学题 =====")
r1 = app.invoke({"messages": [HumanMessage(content="帮我算一下 256 乘以 128 等于多少？")]})
for m in r1["messages"]:
    if hasattr(m, "name") and m.name:
        print(f"  ({m.name}) {m.content}")
    else:
        print(f"  {type(m).__name__}: {m.content}")

# ========== 测试 2：翻译 ==========
print("\n===== 测试 2：翻译 =====")
r2 = app.invoke({"messages": [HumanMessage(content="把这句话翻译成英文：人工智能正在改变世界。")]})
for m in r2["messages"]:
    if hasattr(m, "name") and m.name:
        print(f"  ({m.name}) {m.content}")
    else:
        print(f"  {type(m).__name__}: {m.content}")