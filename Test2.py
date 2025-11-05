from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())

all_items = db.get(include=["documents", "metadatas"])  # removed 'ids'

for doc, meta, _id in zip(all_items["documents"], all_items["metadatas"], all_items["ids"]):
    print(f"ID: {_id}")
    print(f"Metadata: {meta}")
    print(f"Document: {doc[:200]}...")
    print("---")

print(f"Total documents: {len(all_items['documents'])}")
