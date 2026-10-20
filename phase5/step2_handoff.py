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


def sales_agent(state: MessagesState) -> Command[Literal["tech_agent", "__end__"]]:
    print("  [sales_agent] 接待中...")
    system = SystemMessage(
        "你是售前客服，负责处理购买、价格、售后政策咨询。\n"
        "如果用户问的是技术问题（如代码、报错、API 使用），你必须把控制权交给技术客服。\n"
        "遇到技术问题时，只输出：HANDOFF_TECH\n"
        "否则正常回答用户。"
    )
    res = llm.invoke([system] + state["messages"])

    if "HANDOFF_TECH" in res.content:
        print("  [sales_agent] 发现技术问题，移交控制权")
        return Command(
            goto="tech_agent",
            update={"messages":[AIMessage(content="正在为你移交技术客服",name="sales_agent")]},
        )

    print(f"  [sales_agent] 回答: {res.content}")
    return Command(goto=END, update={"messages": [AIMessage(content=res.content, name="sales_agent")]})


def tech_agent(state: MessagesState) -> Command[Literal["__end__"]]:
    print("  [tech_agent] 接手处理...")
    system = SystemMessage("你是技术支持，负责解答代码、API 和技术报错问题。请专业、直接地回答。")
    res = llm.invoke([system] + state["messages"])
    print(f"  [tech_agent] 回答: {res.content}")
    return Command(goto=END, update={"messages": [AIMessage(content=res.content, name="tech_agent")]})


g = StateGraph(MessagesState)
g.add_node("sales_agent", sales_agent)
g.add_node("tech_agent", tech_agent)
g.add_edge(START, "sales_agent")

app = g.compile()

print("===== 测试 1：普通购买咨询 =====")
r1 = app.invoke({"messages": [HumanMessage(content="你们的高级版套餐多少钱一年？")]})
for m in r1["messages"]:
    print(f"  {type(m).__name__}: {m.content}")

print("\n===== 测试 2：技术问题（触发 Handoff） =====")
r2 = app.invoke({"messages": [HumanMessage(content="你们 API 返回 401 报错怎么解决？")]})
for m in r2["messages"]:
    print(f"  {type(m).__name__}: {m.content}")