## 3.1 文档切分：chunk_size 与 chunk_overlap

文件：step1_split.py

第一次（段落+短文本，chunk_size=100）：
- 原始 172 字符，切成 3 块，55/55/58
- overlap 未生效，切分器按 \n\n 段落边界切
- chunk_size 未触发，每段都小于 100

第二次（长文本+无换行，chunk_size=50 改 100）：
- 原始 588 字符，切成 9 块，9/99/100/43/99/100/100/75/60
- overlap 生效，相邻块边界重叠约 20 字符
- chunk_size 生效，每块控制在 100 以内
- chunk 0 只有 9 字符，因中英混排时空格分隔符优先级高于字符

结论：
- chunk_size 是上限，不是目标。段落短于它时不硬凑。
- chunk_overlap 只在硬切时生效。自然边界（段落、句子）切分时不加重叠。
- 中英混排文档，空格分隔符会导致英文单词被单独切出。
- 过短的 chunk 在真实 RAG 里是噪声来源，后续需要处理。


## 3.2 向量化 + Chroma 检索（朴素配置）

文件：step2_embed_store.py

配置：
- Embedding: qwen3.7-text-embedding-flash（通义千问）
- check_embedding_ctx_length=False（关键：网关只接受字符串数组）
- 向量库: Chroma，本地持久化到 ./chroma_db
- 切分: chunk_size=100, chunk_overlap=20

查询：LangGraph 有什么特性？
返回：
  结果 0: "LangGraph"（9 字符碎片）
  结果 1: "异常恢复等复杂问题...LangGraph"

结论：
- 检索能跑通，但结果质量差。
- 9 字符碎片被检索出来，因为它字面含"LangGraph"，向量距离近但语义为零。
- 真正讲"特性"的块（chunk 1/2/4/5/6）一条都没进前 2。
- 根因：chunk_size 太小 + 短碎片污染 + 无 Reranker。

## 待优化
- 调大 chunk_size 到 300
- 加 min_chunk_size 过滤碎片
- 加 Reranker 做二次排序


## 3.3 检索优化：切分参数 + min_chunk_size + LLM rerank

文件：step3_rerank.py

三处改动：
1. chunk_size 100 → 300，chunk_overlap 20 → 50
2. separators 显式加中文标点：。！？；，
3. min_chunk_size=30，过滤碎片
4. 粗筛 k=10，LLM rerank 取 2

查询：LangGraph 有什么特性？
结果：
  候选 0：讲特性、检查点、工具调用、多智能体协作
  候选 1：讲持久化执行、人机协同、记忆、流式输出

对比 3.2：
- 上一轮结果 0 是 9 字符碎片，结果 1 几乎无关。
- 这一轮两条都是语义相关的完整段落。
- chunk_size 大让语义完整；中文分隔符让切点落在句子边界；min_chunk_size 过滤噪声。

## 待优化
- LLM rerank 慢、贵、不稳定，下一轮换 gte-rerank 专门模型
- k=10 在当前小文档上没体现价值，真实项目才有效