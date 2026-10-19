# langgraph_learning

LangGraph 学习轨迹：从 StateGraph 到多 Agent 协作。


## 学习进度

- [x] 环境搭建：PyCharm + GitHub Desktop + .venv + .env
- [x] Phase 1：StateGraph 骨架 + State 机制
  - 替换 / 追加 / Overwrite / MessagesState / 条件边
  - 上下文内容管理并入 Phase 3
- [x] Phase 2：Tool Calling
  - tool_calls 结构 / 手动闭环 / ToolNode / 条件边路由 / Command 路由
  - 结构化 Prompt 与标准内容块并入 Phase 3
- [x] Phase 3：RAG 全链路 + 上下文工程
  - 文档加载 / 切分 / 向量化 / 向量库
  - 多路检索 / Reranker
  - 结构化 Prompt / 标准内容块（content_blocks）
  - 上下文压缩
- [x] Phase 4：Memory / HITL / Middleware
  - Checkpointer：短期记忆 / 长期记忆
  - Human-in-the-Loop：interrupt() + Command(resume=...)
  - Middleware：SummarizationMiddleware / HumanInTheLoopMiddleware / PIIMiddleware
  - UntrackedValue：不被 checkpoint 的 State 字段
- [ ] Phase 5：多 Agent + MCP
  - Supervisor / Worker 模式
  - Handoff：Command(graph=Command.PARENT)
  - MCP：langchain.mcp（v1 规范，无状态）
  - create_agent：LangChain v1 标准入口
- [ ] Phase 6：可观测性 + 评估 + 部署
  - LangSmith / Langfuse Tracing
  - Agent Eval
  - Docker 部署

## 说明

- Phase 1、2 中未做的“上下文内容管理”和“结构化 Prompt”已并入 Phase 3。
- Middleware 是 LangChain v1 的定义性特性，已并入 Phase 4。
- MCP 已移入 langchain 主包（langchain.mcp），Phase 5 以 v1 规范为准。
- UntrackedValue 是 State 字段的第四种行为，Phase 4 补齐。

## 环境

- Python 3.11
- langgraph 1.2.15
- langchain-core 1.6.10


## 待补清单（留到项目阶段）

以下内容已在学习中明确识别，但**暂不在此仓库实现**，留到后续项目仓库：

### 检索优化
- [ ] 混合检索（dense 向量 + BM25 关键词并行）
- [ ] RRF（倒数排序融合）合并两路结果
- [ ] 专用 Cross-Encoder Reranker（如 bge-reranker-v2-m3）替换 LLM rerank
- [ ] 动态阈值截断（只保留分数达标的 Top 3-5）
- [ ] 查询改写 / 多子查询分解

### 上下文工程
- [ ] 上下文压缩（对话历史 / 检索结果过长时的截断与摘要）
- [ ] SummarizationMiddleware（LangChain v1 内置）

### 触发时机
- 项目阶段，当文档规模超过单篇小文档、检索质量可被量化评估时引入。
- 每引入一项，需配套 eval harness（黄金集 + 指标）验证其贡献。