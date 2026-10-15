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


## 2.2 手动跑通 Tool Calling 完整闭环

文件：tool_call_full.py

三步流程：

1. 模型发出 tool_calls（content 为空）
2. 手动执行工具，包成 ToolMessage 回传
3. 把完整 messages 再交给模型，生成最终回答

输出：

    第一轮 tool_calls: [{'name': 'get_weather', 'args': {'city': '北京'}, 'id': 'call_...', 'type': 'tool_call'}]
    [tool] get_weather(city=北京) -> 晴，25°C
    最终回答: 北京今天天气：晴，气温 25°C。适合外出，注意防晒和补水。

结论：
- 模型第二次被调用时，messages 里多了 AI 调用请求和 ToolMessage 两条。
- ToolMessage 必须带 tool_call_id，与 tc["id"] 对应。
- 模型不执行工具，只负责决策和生成最终回答。
- 执行工具、拼 ToolMessage 是开发者（或框架）的责任。

## 待验证
- LangGraph 的 ToolNode 如何自动完成第 2 步？
- 图里如何根据 tool_calls 是否为空做路由？


## 待验证
- 工具执行结果怎么包成 ToolMessage 回传给模型？
- 图里怎么根据 tool_calls 是否为空做路由？