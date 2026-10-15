from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

with open("sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

doc = Document(page_content=text, metadata={"source": "sample.txt"})
print("原始文档长度:", len(doc.page_content))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
)
chunks = splitter.split_documents([doc])

print(f"切成了 {len(chunks)} 块")
for i, c in enumerate(chunks):
    print(f"\n--- chunk {i} (len={len(c.page_content)}) ---")
    print(c.page_content)