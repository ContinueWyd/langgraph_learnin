# Phase 2：Tool Calling

## 2.1 bind_tools 后模型返回 tool_calls 而非文本

文件：tool_call_raw.py
输入：北京今天天气怎么样？

输出：

    content: 
    tool_calls: [{'name': 'get_weather', 'args': {'city': '北京'}, 'id': 'call_00_...', 'type': 'tool_call'}]

结论：
- 绑定工具后，模型判断需要调工具时，content 为空，返回结构化的 tool_calls。
- tool_calls 字段：name（函数名）、args（模型抽取的参数）、id（调用标识，回传结果时要用）。
- 参数由模型从自然语言中抽取，依据是 @tool 函数的签名和 docstring。
- 这是 Agent 的数据基础：路由、执行、回传都围绕 tool_calls 展开。

## 待验证
- 工具执行结果怎么包成 ToolMessage 回传给模型？
- 图里怎么根据 tool_calls 是否为空做路由？