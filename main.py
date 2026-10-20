import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# 1. 初始化 FastAPI
app = FastAPI(title="LangGraph Weather Agent API")

# 2. 定义请求体格式
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default-user"

# 3. 定义工具
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    return f"{city}：晴，25°C"

# 4. 构建 LangGraph 图
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)
llm_with_tools = llm.bind_tools([get_weather])

def agent_node(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: MessagesState) -> str:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

g = StateGraph(MessagesState)
g.add_node("agent", agent_node)
g.add_node("tools", ToolNode([get_weather]))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

# 注意：生产环境这里通常用 SqliteSaver 或 PostgresSaver
graph_app = g.compile(checkpointer=InMemorySaver())

# 5. 提供 HTTP 接口
# 注意：去掉 async
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        result = graph_app.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config
        )
        answer = result["messages"][-1].content
        return {"status": "success", "answer": answer, "thread_id": request.thread_id}
    except Exception as e:
        print("报错:", str(e))  # 打印到 docker logs 方便排查
        raise HTTPException(status_code=500, detail=str(e))