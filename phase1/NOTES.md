# Phase 1：StateGraph 骨架 + 上下文结构

## 1.1 Annotated[list, add] 的追加行为

文件：first_graph.py
输入：{"messages": ["用户输入"]}

输出：

    node_1 收到: ['用户输入']
    node_2 收到: ['用户输入', 'node_1 说的话']
    最终结果: {'messages': ['用户输入', 'node_1 说的话', 'node_2 说的话']}

结论：节点返回的新列表被追加到旧列表尾部，顺序按节点执行顺序排列。

## 1.2 无 reducer 时的替换行为

文件：no_reducer.py
输入：同 1.1

输出：

    node_1 收到: ['用户输入']
    node_2 收到: ['node_1 说的话']
    最终结果: {'messages': ['node_2 说的话']}

结论：去掉 Annotated[list, add] 后，默认行为是替换。每经过一个节点，前一条消息被覆盖。最终只剩最后一条。

## 1.3 对比

| 项目 | 有 reducer | 无 reducer |
|---|---|---|
| node_2 收到 | 2 条 | 1 条 |
| 最终结果 | 3 条 | 1 条 |

为什么重要：Agent 的多步推理依赖历史累积。没有 reducer，每步都会丢失上文。

## 待验证

- Overwrite：想清空合并型字段，返回 [] 是否无效？