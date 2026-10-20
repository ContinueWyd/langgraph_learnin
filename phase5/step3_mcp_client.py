import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

async def main():
    # 1. 启动并连接 MCP Server
    client = MultiServerMCPClient(
        {
            "demo": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )

    # 2. 动态发现工具
    tools = await client.get_tools()
    print(f"发现工具: {[t.name for t in tools]}")

    # 3. 挂载到 Agent
    agent = create_agent(model=llm, tools=tools)

    # 4. 测试
    print("\n===== 测试 1：加法 =====")
    r1 = await agent.ainvoke({"messages": [("user", "帮我算一下 42 加 58 等于多少？")]})
    print("  回答:", r1["messages"][-1].content)

    print("\n===== 测试 2：打招呼 =====")
    r2 = await agent.ainvoke({"messages": [("user", "请对小明说一句欢迎语。")]})
    print("  回答:", r2["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())