import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore
from langgraph.runtime import Runtime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

def chat_node(state: MessagesState, runtime: Runtime):
    user_id = runtime.context.get("user_id", "anonymous")
    namespace = ("preferences", user_id)

    # 1. 从 store 读已存的偏好
    prefs = runtime.store.search(namespace)
    pref_text = ""
    if prefs:
        pref_text = "；".join(p.value.get("text", "") for p in prefs)
        print(f"  [chat_node] 读到偏好: {pref_text}")

    # 2. 拼 system prompt
    messages = []
    if pref_text:
        messages.append(("system", f"用户偏好：{pref_text}"))
    messages.extend(state["messages"])

    # 3. 简单规则：如果用户说"我喜欢/我偏好"，存进 store
    last = state["messages"][-1].content
    if "我喜欢" in last or "我偏好" in last:
        runtime.store.put(namespace, key="pref_1", value={"text": last})
        print(f"  [chat_node] 已存入偏好: {last}")

    response = llm.invoke(messages)
    return {"messages": [response]}

g = StateGraph(MessagesState)
g.add_node("chat", chat_node)
g.add_edge(START, "chat")
g.add_edge("chat", END)

with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer, \
     SqliteStore.from_conn_string("store.db") as store:

    app = g.compile(checkpointer=checkpointer, store=store)

    print("===== 第一轮（thread_id=user-1）：声明偏好 =====")
    r1 = app.invoke(
        {"messages": [HumanMessage(content="我喜欢用中文回答")]},
        config={"configurable": {"thread_id": "user-1"}},
        context={"user_id": "xiaoming"},  # ← 作为第三个参数单独传
    )
    print("  回答:", r1["messages"][-1].content)

    print("\n===== 第二轮（thread_id=user-2）：换会话，看是否还记得偏好 =====")
    r2 = app.invoke(
        {"messages": [HumanMessage(content="请回答我的问题：1+1等于几？")]},
        config={"configurable": {"thread_id": "user-2"}},
        context={"user_id": "xiaoming"},
    )
    print("  回答:", r2["messages"][-1].content)