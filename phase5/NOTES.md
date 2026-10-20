# Phase 5：多 Agent + MCP

## 5.1 Supervisor / Worker 模式：基础多 Agent 协作

文件：step1_supervisor.py

图结构：
  START → supervisor → (Command goto)
                          ├── math_worker → supervisor（回边）
                          ├── text_worker → supervisor（回边）
                          └── END

输出：
测试 1（数学）: supervisor → math → supervisor → done
测试 2（翻译）: supervisor → text → supervisor → done

结论：
- Supervisor 被调用两次：第一次派活，第二次验收。
- Worker 干完活必须回到 Supervisor（回边），由中心节点决定下一步。
- AIMessage 的 name 字段保留，便于 Supervisor 识别谁已回答。
- 结束条件由模型判断（输出 done）。

## 待优化
- 用 with_structured_output 替代强 Prompt 约束，防止模型输出不合法导致中断。


## 5.2 Handoff 模式：Agent 间直接移交控制权

文件：step2_handoff.py

图结构：
  START → sales_agent ──┬── Command(goto="tech_agent") → tech_agent → END
                        └── Command(goto=END) → END

输出：
测试 1: sales_agent 自己回答，未触发交接。
测试 2: sales_agent 识别出技术问题，输出 HANDOFF_TECH，移交 tech_agent 处理。

结论：
- Handoff 是点对点交接，不需要中心 Supervisor 调度。
- 适合链式流转（售前→售后→技术）。
- 原 Agent 交接后直接“退休”，不再参与后续。
- 交接时可选择是否写入一条“正在转接”的消息给用户。

## Supervisor vs Handoff
| 模式 | 拓扑 | 调度者 | 场景 |
|---|---|---|---|
| Supervisor | 星型 | 中心节点 | 复杂多任务分发 |
| Handoff | 链型/网状 | 无中心 | 线性流程/客服流转 |