import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

with open("sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = Document(page_content=text, metadata={"source": "sample.txt"})

splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_documents([doc])
print(f"切分完成，共 {len(chunks)} 块")

# 1. Embedding 模型
embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBED_MODEL_NAME"),
    base_url=os.getenv("EMBED_BASE_URL"),
    api_key=os.getenv("EMBED_API_KEY"),
    check_embedding_ctx_length=False,
)
print("Embedding 模型初始化完成")

# 2. 存进 Chroma（会自动调用 Embeddings 把每块转向量）
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)
print("已写入向量库")

# 3. 检索
query = "LangGraph 有什么特性？"
results = vectorstore.similarity_search(query, k=2)

print(f"\n查询：{query}")
print(f"返回 {len(results)} 条：")
for i, r in enumerate(results):
    print(f"\n--- 结果 {i} (来源: {r.metadata.get('source')}) ---")
    print(r.page_content)