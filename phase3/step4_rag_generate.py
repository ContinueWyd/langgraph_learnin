import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma

load_dotenv()

# 1. 复用 3.3 的切分和向量库
with open("sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = Document(page_content=text, metadata={"source": "sample.txt"})

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", ""],
)
chunks = splitter.split_documents([doc])
chunks = [c for c in chunks if len(c.page_content.strip()) >= 30]

embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBED_MODEL_NAME"),
    base_url=os.getenv("EMBED_BASE_URL"),
    api_key=os.getenv("EMBED_API_KEY"),
    check_embedding_ctx_length=False,
)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db_v3",
)

# 2. 检索
query = "LangGraph 有什么特性？"
docs = vectorstore.similarity_search(query, k=2)

# 3. 结构化 Prompt：资料 / 问题 / 指令 分区
context = "\n\n".join(d.page_content for d in docs)

prompt = f"""<资料>
{context}
</资料>

<问题>
{query}
</问题>

<指令>
只根据上面的资料回答问题。如果资料里没有相关信息，回答"资料中未提及"。
不要编造资料里没有的内容。
</指令>
"""

print("===== Prompt 全文 =====")
print(prompt)
print("===== 模型回答 =====")

# 4. 调模型
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)
response = llm.invoke(prompt)
print(response.content)