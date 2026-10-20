import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from typing import Literal

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)


# ======== 埋雷 1：会报错的工具 ========
@tool
def search_web(query: str) -> str:
    """搜索互联网。"""
    print("  [tool] search_web 正在执行...")
    time.sleep(1)  # 模拟网络延迟
    raise ValueError("网络连接超时：无法访问外部搜索 API。")  # 故意抛错


@tool
def calculate(expr: str) -> str:
    """计算数学表达式。"""
    print("  [tool] calculate 正在执行...")
    return "结果：42"


tools = [search_web, calculate]
llm_with_tools = llm.bind_tools(tools)


# ======== Supervisor 节点 ========
def supervisor_node(state: MessagesState) -> Command[Literal["tools", "__end__"]]:
    print("  [supervisor] 正在思考下一步...")

    # 如果最后一条是工具报错，模型可能会不知所措，这里我们故意诱导它重试
    system = SystemMessage(content="如果工具执行失败，请再试一次搜索。如果重试了3次还不行，就放弃并回答结束。")

    # 注意：如果是第一次进来，不带 system；如果是带着工具报错回来，带上 system
    messages = state["messages"]
    if len(messages) > 0 and isinstance(messages[-1], ToolMessage):
        messages = [system] + messages

    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        print(f"  [supervisor] 决定调用工具: {response.tool_calls[0]['name']}")
        return Command(goto="tools", update={"messages": [response]})
    else:
        print("  [supervisor] 决定结束回答")
        return Command(goto=END, update={"messages": [response]})


# ======== 搭图 ========
g = StateGraph(MessagesState)
g.add_node("supervisor", supervisor_node)
g.add_node("tools", ToolNode(tools))

g.add_edge(START, "supervisor")
g.add_edge("tools", "supervisor")

app = g.compile()

# ======== 执行 ========
print("===== 开始执行（请观察报错与循环） =====")
try:
    result = app.invoke({"messages": [HumanMessage(content="帮我搜一下今天的新闻。")]})
    print("\n最终回答:", result["messages"][-1].content)
except Exception as e:
    print(f"\n程序崩溃了，报错信息: {type(e).__name__}: {e}")