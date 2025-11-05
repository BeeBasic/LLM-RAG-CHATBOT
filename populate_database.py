# populate_database.py
import argparse
import os
import shutil
import typing as t
import warnings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma

# === Global constants ===
CHROMA_PATH = "chroma"
DATA_PATH = "data"
BATCH_SIZE = 2000  # safe batch limit for Chroma inserts

# Suppress PyPDF2 spam about duplicate /Info fields
warnings.filterwarnings("ignore", category=UserWarning, module="PyPDF2")


def main():
    """CLI entry point for populating or resetting the Chroma database."""
    parser = argparse.ArgumentParser(description="Populate or reset Chroma vector database.")
    parser.add_argument("--reset", action="store_true", help="Reset (clear) the database before repopulating.")
    args = parser.parse_args()

    if args.reset:
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents() -> t.List[Document]:
    """Load all PDFs from the data directory."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Data directory '{DATA_PATH}' not found.")
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    print(f"📄 Loaded {len(documents)} documents from '{DATA_PATH}'")
    return documents


def split_documents(documents: t.List[Document]) -> t.List[Document]:
    """Split documents into smaller text chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks total")
    return chunks


def add_to_chroma(chunks: t.List[Document]):
    """Add chunks to the Chroma vector database in safe batches."""
    if not chunks:
        print("⚠️ No chunks to add. Exiting.")
        return

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get existing document IDs to avoid duplicates
    existing_items = db.get(include=[])  # IDs are always returned
    existing_ids = set(existing_items.get("ids", []))
    print(f"📦 Existing documents in DB: {len(existing_ids)}")

    # Filter out already-added chunks
    new_chunks = []
    chunks_per_file = {}
    for chunk in chunks_with_ids:
        chunk_id = chunk.metadata.get("id")
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)
            source_file = chunk.metadata.get("source", "unknown")
            chunks_per_file[source_file] = chunks_per_file.get(source_file, 0) + 1

    if not new_chunks:
        print("✅ No new documents to add. Database is up to date.")
        return

    print(f"👉 Adding {len(new_chunks)} new chunks across {len(chunks_per_file)} files")
    for file, count in chunks_per_file.items():
        print(f"   {os.path.basename(file)} — {count} chunks")

    # Generate IDs for new chunks
    new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

    # === Batch insert to avoid Chroma's internal 5461 limit ===
    for i in range(0, len(new_chunks), BATCH_SIZE):
        batch_chunks = new_chunks[i:i + BATCH_SIZE]
        batch_ids = new_chunk_ids[i:i + BATCH_SIZE]
        print(f"🧩 Inserting batch {i // BATCH_SIZE + 1} — {len(batch_chunks)} chunks...")
        db.add_documents(batch_chunks, ids=batch_ids)

    print("✅ Database successfully populated and saved to disk!")


def calculate_chunk_ids(chunks: t.List[Document]) -> t.List[Document]:
    """Generate unique IDs for each chunk based on source and page."""
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", 0)
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

    return chunks


def clear_database():
    """Delete existing Chroma database directory."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"🗑️ Cleared old Chroma database at '{CHROMA_PATH}'")
    else:
        print("⚠️ No existing database found to clear.")


if __name__ == "__main__":
    main()
