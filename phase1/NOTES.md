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


## 1.4 Overwrite 实验：返回 [] 无法清空

文件：overwrite_test.py
输入：{"messages": ["用户输入"]}

输出：

    clear_node 收到: ['用户输入', 'node_1 说的话']
    node_2 收到: ['用户输入', 'node_1 说的话']
    最终结果: {'messages': ['用户输入', 'node_1 说的话', 'node_2 说的话']}

结论：clear_node 返回 []，但 reducer 执行的是 add(旧值, [])，结果等于旧值。返回空列表无法清空合并型字段。要清空必须用 Overwrite([]) 绕过 reducer。

## 1.5 Overwrite 生效：绕过 reducer 清空

文件：overwrite_real.py
输入：{"messages": ["用户输入"]}

输出：

    clear_node 收到: ['用户输入', 'node_1 说的话']
    node_2 收到: []
    最终结果: {'messages': ['node_2 说的话']}

结论：Overwrite([]) 绕过 add reducer，直接替换字段值。清空效果在下一个节点可见，clear_node 自身读到的仍是上游历史。

## 1.6 三种字段控制方式对比

| 声明方式 | 行为 | 适用场景 |
|---|---|---|
| messages: list | 每步替换 | 只关心最新值的字段 |
| Annotated[list, add] | 每步追加 | 对话历史、工具调用记录 |
| Overwrite(...) | 强制替换 | 需要中途重置上下文的场景 |


## 1.7 MessagesState：内置的消息状态

文件：messages_state.py
输入：{"messages": [HumanMessage(content="用户输入")]}

输出：

    node_1 收到: [HumanMessage(content='用户输入', ...)]
    node_2 收到: [HumanMessage(...), AIMessage(content='node_1 说的话', ...)]
    最终结果:
      HumanMessage -> 用户输入
      AIMessage -> node_1 说的话
      AIMessage -> node_2 说的话

结论：MessagesState 等价于 messages: Annotated[list, add]，但消息是对象而非字符串。对象带 type（Human/AI/Tool）、id、tool_calls 等字段，tool_calls 是 Phase 2 工具调用的载体。

## Phase 1 State 部分小结

| 声明方式 | 行为 | 场景 |
|---|---|---|
| messages: list | 替换 | 只关心最新值 |
| Annotated[list, add] | 追加 | 对话历史 |
| MessagesState | 追加 + 消息对象 | 所有对话型 Agent |
| Overwrite(...) | 强制替换 | 中途重置上下文 |


## 1.8 条件边：运行时决定分支

文件：conditional_edge.py

图结构：

    START → router → (route_decision)
                        ├── "greet"    → greet    → END
                        └── "farewell" → farewell → END

输入1：{"messages": [HumanMessage(content="你好")]}
输出1：最后一条 = "你好，我是 greet 分支"

输入2：{"messages": [HumanMessage(content="拜拜")]}
输出2：最后一条 = "再见，我是 farewell 分支"

结论：
- route_decision 不是节点，是挂在 router 后的判断函数，返回字符串决定走哪条边。
- 条件边互斥，每次运行只走一条分支。
- router_node 返回 {}，不修改 State，说明节点可以只做判断不做写操作。
- 这是 Agent 的骨架：Phase 2 会把 if 判断换成模型输出。

## Phase 1 完成清单

- [x] 1.1 Annotated[list, add] 追加
- [x] 1.2 无 reducer 替换
- [x] 1.3 对比
- [x] 1.4 返回 [] 无法清空
- [x] 1.5 Overwrite 绕过 reducer
- [x] 1.6 三种控制方式对比
- [x] 1.7 MessagesState
- [x] 1.8 条件边

