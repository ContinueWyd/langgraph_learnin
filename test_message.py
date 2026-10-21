from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    AnyMessage
)
import json


def print_msg(title: str, msg):
    print(f"\n================ {title} ================")
    print(f"1. 消息类型: {type(msg).__name__}")
    print(f"2. content内容: {repr(msg.content)}")
    print(f"3. name属性: {getattr(msg, 'name', None)}")

    # 如果是 AIMessage 且带有工具调用
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"4. tool_calls: {msg.tool_calls}")

    # 如果是 ToolMessage
    if hasattr(msg, "tool_call_id") and msg.tool_call_id:
        print(f"5. tool_call_id: {msg.tool_call_id}")

    # 打印底层转成字典的样子（这就是发给大模型时的真实格式）
    print(f"6. 底层字典格式:\n{json.dumps(msg.model_dump(), ensure_ascii=False, indent=2, default=str)}")


def main():
    # 1. SystemMessage (系统指令)
    system_msg = SystemMessage(content="你是一个天气助手。")
    print_msg("SystemMessage", system_msg)

    # 2. HumanMessage (用户输入)
    human_msg = HumanMessage(content="北京天气怎么样？", name="user_123")
    print_msg("HumanMessage", human_msg)

    # 3. AIMessage (纯文本回答)
    ai_text_msg = AIMessage(content="北京今天晴天，25度。", name="weather_agent")
    print_msg("AIMessage (纯文本)", ai_text_msg)

    # 4. AIMessage (发起工具调用)
    ai_tool_call_msg = AIMessage(
        content="",  # 发起调用时 content 通常为空
        tool_calls=[
            {
                "name": "get_weather",
                "args": {"city": "北京"},
                "id": "call_abc123",
                "type": "tool_call"
            }
        ]
    )
    print_msg("AIMessage (工具调用)", ai_tool_call_msg)

    # 5. ToolMessage (工具执行结果)
    tool_msg = ToolMessage(
        content="晴，25°C",
        tool_call_id="call_abc123",
        name="get_weather"
    )
    print_msg("ToolMessage", tool_msg)

    # 6. 元组简写转换测试
    print("\n================ 元组简写测试 ================")
    tuples = [
        ("system", "你是翻译专家"),
        ("user", "翻译一下apple"),
        ("assistant", "苹果")
    ]

    # LangChain 内部会自动映射
    print("原始元组列表:", tuples)
    # 如果你要手动转，可以使用 langchain_core.messages.convert_to_messages
    from langchain_core.messages import convert_to_messages
    converted_msgs = convert_to_messages(tuples)
    print("转换后的对象列表:")
    for m in converted_msgs:
        print(f"  - {type(m).__name__}: {m.content}")


if __name__ == "__main__":
    main()