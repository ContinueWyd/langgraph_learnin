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



## 4.3 长期记忆：Store 跨 thread_id 持久化

文件：long_term_memory.py

配置：
- SqliteStore.from_conn_string("store.db")，独立于 checkpointer
- g.compile(checkpointer=checkpointer, store=store)
- invoke 的 context 参数传 user_id（注意：不是放在 config 里）

输出：
第一轮（thread_id=user-1, user_id=xiaoming）:
  读到偏好 → 已存入偏好 → "好的，小明，我会继续用中文回答。"
第二轮（thread_id=user-2, user_id=xiaoming）:
  读到偏好 → "1+1等于2。"

结论：
- 换 thread_id 后，checkpointer 的历史不共享，但 store 的偏好共享。
- namespace 按 ("preferences", user_id) 隔离，不同用户数据互不干扰。
- context 参数必须作为 invoke 的独立参数传入，不能放在 config 里。
- store.db 也是持久化的，跨脚本累积。

## 两层记忆对比

| | Checkpointer | Store |
|---|---|---|
| 隔离键 | thread_id | namespace |
| 存什么 | 会话历史 | 用户长期数据 |
| 第二轮能否看到 | 否（新 thread） | 是（同 user_id） |
| 文件 | checkpoints.db | store.db |

## 待验证
- 用更明显的场景（如"用一句话介绍自己"）验证偏好真的影响输出。



## 4.4 Human-in-the-Loop：interrupt 暂停 + Command(resume) 恢复

文件：step4_hitl.py

第一次 invoke：
  跑到 approval_node 的 interrupt() 暂停，step3 未执行。
  返回里多出 __interrupt__ 字段，含 question、details、id。

第二次 invoke（Command(resume="yes")）：
  approval_node 被重新执行，interrupt 前的 print 又打印一次。
  interrupt() 直接返回 "yes" 不暂停，图继续跑到 END。
  最终 messages 4 条：Human + step1 + approval + step3。

结论：
- interrupt() 让图在节点内暂停，把控制权交回人类。
- 恢复靠 Command(resume=...)，配合同一个 thread_id。
- 被中断的节点恢复时会从头重新执行，interrupt 之前的代码必须幂等。
- __interrupt__ 字段含中断信息，id 用于定位。

## 待验证
- interrupt 前的非幂等操作会导致重复执行（真实项目需注意）。
- 多个 interrupt 串联的场景。

## 4.5 Middleware：SummarizationMiddleware 上下文压缩

文件：step5_middleware.py

配置：
- create_agent(model, tools=[], middleware=[summarizer], checkpointer=InMemorySaver())
- SummarizationMiddleware(model=llm, trigger=("tokens", 100), keep=("messages", 2))
- invoke 传 config={"configurable": {"thread_id": "summary-test-1"}}

输出（trigger=100）：
第 1 轮: 2 条
第 2 轮: 4 条
第 3-8 轮: 4 条（稳定，不再增长）

对比 trigger=500：
第 1-8 轮: 2,4,6,8,10,12,14,16 线性增长，摘要从未触发

结论：
- SummarizationMiddleware 在 token 超过 trigger 时，把旧消息摘要成一条，只保留最近 keep 条。
- 摘要让上下文长度稳定，不再无限增长。
- trigger 阈值决定摘要介入时机。太低会频繁摘要，太高则从不触发。
- 摘要是有损的，细节会丢失。真实项目需用 eval 验证参数。

## 待验证
- 摘要的具体结构（保留几条原文 + 摘要条数）
- 多个 Middleware 串联的场景（如 PII 脱敏 + 摘要）