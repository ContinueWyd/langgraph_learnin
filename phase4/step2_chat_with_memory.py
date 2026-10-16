import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

def chat_node(state: MessagesState):
    print(f"  [chat_node] 收到 {len(state['messages'])} 条消息")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

g = StateGraph(MessagesState)
g.add_node("chat", chat_node)
g.add_edge(START, "chat")
g.add_edge("chat", END)

with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    app = g.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "user-1"}}

    print("===== 第一轮：自我介绍 =====")
    r1 = app.invoke({"messages": [HumanMessage(content="我叫小明，请记住。")]}, config)
    print("  模型回答:", r1["messages"][-1].content)

    print("\n===== 第二轮：问名字（同一 thread_id） =====")
    r2 = app.invoke({"messages": [HumanMessage(content="我叫什么？")]}, config)
    print("  模型回答:", r2["messages"][-1].content)

    print("\n===== 第三轮：换 thread_id 再问 =====")
    config2 = {"configurable": {"thread_id": "user-2"}}
    r3 = app.invoke({"messages": [HumanMessage(content="我叫什么？")]}, config2)
    print("  模型回答:", r3["messages"][-1].content)