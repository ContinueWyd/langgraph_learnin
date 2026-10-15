import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    fake_db = {"北京": "晴，25°C", "上海": "小雨，22°C"}
    result = fake_db.get(city, f"{city}：暂无数据")
    print(f"[tool] get_weather(city={city}) -> {result}")
    return result

llm = init_chat_model(
    model=os.getenv("MODEL_NAME"),
    model_provider="openai",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

llm_with_tools = llm.bind_tools([get_weather])

messages = [HumanMessage(content="北京今天天气怎么样？")]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

print("第一轮 tool_calls:", ai_msg.tool_calls)

for tc in ai_msg.tool_calls:
    result = get_weather.invoke(tc["args"])
    messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

final = llm_with_tools.invoke(messages)
print("最终回答:", final.content)