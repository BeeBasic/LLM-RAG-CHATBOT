import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader  # Updated import
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma

CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():
    # CLI argument for resetting database
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Load, split, and add documents
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    print(f"📄 Loaded {len(documents)} PDFs from {DATA_PATH}")
    return documents


def split_documents(documents: list[Document]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks")
    return chunks


def add_to_chroma(chunks: list[Document]):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())

    # Assign unique IDs to chunks
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Find existing documents
    existing_items = db.get(include=[])  # IDs are always returned
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add new chunks
    new_chunks = []
    chunks_per_file = {}
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
            source_file = chunk.metadata.get("source", "unknown")
            chunks_per_file[source_file] = chunks_per_file.get(source_file, 0) + 1

    if len(new_chunks):
        print(f"👉 Adding {len(new_chunks)} new chunks")
        for file, count in chunks_per_file.items():
            print(f"   {file}: {count} chunks")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"🗑️ Cleared {CHROMA_PATH} database")


if __name__ == "__main__":
    main()
