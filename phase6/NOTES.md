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