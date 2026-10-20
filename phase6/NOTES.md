# Phase 6：可观测性 + 评估 + 部署

## 6.1 接入 LangSmith 实现零代码侵入追踪

文件：step1_tracing.py

配置（.env）：
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_xxx
# 未配置 LANGCHAIN_PROJECT，默认落在 default 项目

输出（LangSmith 网页端截图）：
- 自动生成可视化执行树：agent → should_continue → tools → agent
- 显示每次模型调用的耗时（4.34s, 3.48s）
- 显示 Token 消耗（393, 436）
- 记录工具调用的参数（city: 北京）和返回结果

结论：
- LangSmith 实现了零代码侵入追踪，无需改任何业务逻辑。
- 对调试多节点、多 Agent 循环非常重要，能看清每次调用的耗时、Token、输入输出。
- 终端可能因为网络超时打印报错，只要网页端能看就行（或开启代理解决）。


## 6.2 复杂报错场景下的 Tracing 排查

文件：step2_debug_tracing.py

场景：
故意在 `search_web` 工具中抛出 `ValueError("网络连接超时...")`。
终端输出显示工具并行执行时抛出异常，程序直接崩溃。

LangSmith 截图观察：
- 整体 Trace 标红，顶部直接显示 `Error` 标签。
- 左侧执行树中，`tools` 节点下的 `search_web` 带有红色错误标记。
- 点击错误节点，右侧直接显示 `ValueError` 及完整 Traceback。

结论：
- 在复杂循环或并行调用中，终端日志往往难以定位根因。
- LangSmith 能直观呈现调用链路（谁调用了谁）、耗时，并高亮错误节点，极大降低排错成本。


## 6.3 自动化评估（Eval）基础

文件：step3_eval.py

流程：
1. 定义黄金测试集 TEST_DATASET（包含 input 和 expected）。
2. 定义评估器 evaluate_answer（判断 expected 是否在 actual 中）。
3. 遍历测试集，调用模型，对比结果，输出通过率。

输出：
Test 1: PASS
Test 2: PASS
Test 3: PASS
通过率: 3/3 (100.0%)

结论：
- Eval 的核心是：黄金测试集 + 评估逻辑。
- 简单的字符串包含判断能处理基础场景。
- 真实生产环境会用 LLM-as-a-Judge（用大模型做语义匹配），或接入 LangSmith 的 Eval 模块。
- 有了 Eval，修改 Prompt 或换模型后，才能量化评估“是否变好了”。