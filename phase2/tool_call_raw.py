import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    fake_db = {"北京": "晴，25°C", "上海": "小雨，22°C"}
    return fake_db.get(city, f"{city}：暂无数据")

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://www.micuapi.ai/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

llm_with_tools = llm.bind_tools([get_weather])

response = llm_with_tools.invoke("北京今天天气怎么样？")
print("content:", response.content)
print("tool_calls:", response.tool_calls)