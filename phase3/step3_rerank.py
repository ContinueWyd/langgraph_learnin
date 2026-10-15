import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma

load_dotenv()

# 1. 读文档 + 优化后的切分
with open("sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = Document(page_content=text, metadata={"source": "sample.txt"})

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", ""],
)
chunks = splitter.split_documents([doc])
# 过滤短块
chunks = [c for c in chunks if len(c.page_content.strip()) >= 30]
print(f"切分完成，共 {len(chunks)} 块")
for i, c in enumerate(chunks):
    print(f"  chunk {i}: len={len(c.page_content)}")

# 2. Embedding + Chroma
embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBED_MODEL_NAME"),
    base_url=os.getenv("EMBED_BASE_URL"),
    api_key=os.getenv("EMBED_API_KEY"),
    check_embedding_ctx_length=False,
)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db_v2",
)

# 3. 粗筛 k=10
query = "LangGraph 有什么特性？"
candidates = vectorstore.similarity_search(query, k=10)
print(f"\n粗筛返回 {len(candidates)} 条")

# 4. LLM rerank：让模型从候选里选最相关的 2 条
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)

candidates_text = "\n\n".join(
    f"[{i}] {c.page_content}" for i, c in enumerate(candidates)
)
rerank_prompt = f"""下面有 {len(candidates)} 段候选文本，请选出与问题最相关的 2 段的编号。
只输出编号，用逗号分隔，例如：0,3

问题：{query}

候选：
{candidates_text}
"""
response = llm.invoke(rerank_prompt)
print("LLM 选择:", response.content)

# 5. 取出被选中的
import re
ids = [int(x) for x in re.findall(r"\d+", response.content)][:2]
print(f"\n最终返回 {len(ids)} 条：")
for i in ids:
    print(f"\n--- 候选 {i} ---")
    print(candidates[i].page_content)