# Phase 4：Memory / HITL / Middleware

## 4.1 Checkpointer：短期记忆的存储层

文件：step1_checkpointer.py

配置：
- SqliteSaver.from_conn_string("checkpoints.db")
- g.compile(checkpointer=checkpointer)
- config = {"configurable": {"thread_id": "user-1"}}

输出：
第一轮（user-1）: echo_node 收到 1 条 → 最终 2 条
第二轮（user-1）: echo_node 收到 3 条 → 最终 4 条
第三轮（user-2）: echo_node 收到 1 条 → 最终 2 条

结论：
- 同一 thread_id 的多次 invoke 共享 State，历史跨 invoke 累积。
- 不同 thread_id 完全隔离，新会话从零开始。
- 最终消息数 = 收到数 + 1，节点返回的 AIMessage 被追加（reducer 行为）。
- Checkpointer 只负责存取 State，不负责理解内容。理解由模型完成。

## 待验证
- 把 echo_node 换成真实模型调用，验证模型能否基于历史回答。
- 长期记忆（store）跨 thread_id 的实现。


## 4.2 模型 + Checkpointer：真正的记忆

文件：step2_chat_with_memory.py

输出：
第一轮（user-1）: chat_node 收到 5 条 → "记住了，你叫小明"
第二轮（user-1）: chat_node 收到 7 条 → "你叫小明"
第三轮（user-2）: chat_node 收到 3 条 → "我不知道你的名字"

结论：
- 节点里把 state["messages"] 完整发给模型，模型就能基于历史回答。
- checkpointer 只负责存取，理解由模型完成。两者结合才是真正的记忆。
- 同一 thread_id 的历史跨脚本、跨运行累积（checkpoints.db 持久化）。
- State 会无限累积，需要上下文压缩（留到项目阶段）。

## 对比 4.1
| 节点 | 第二轮回答 | 是否真正记得 |
|---|---|---|
| echo_node | "你说的是：我叫什么？" | 否 |
| chat_node | "你叫小明。" | 是 |