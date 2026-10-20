from mcp.server.fastmcp import FastMCP

# 1. 创建 MCP Server
mcp = FastMCP("demo-server")

# 2. 用装饰器注册工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个数字的和。"""
    return a + b

@mcp.tool()
def greet(name: str) -> str:
    """向指定的人打招呼。"""
    return f"你好，{name}！欢迎使用 MCP。"

# 3. 启动 Server（走 stdio 通信）
if __name__ == "__main__":
    mcp.run()