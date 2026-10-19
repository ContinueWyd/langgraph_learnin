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