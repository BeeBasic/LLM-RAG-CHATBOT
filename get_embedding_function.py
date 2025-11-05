# get_embedding_function.py
from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    """
    Returns an embeddings callable compatible with Chroma/langchain.
    Current choice: nomic-embed-text via OllamaEmbeddings.
    """
    # Model name here must match what you have locally available via Ollama
    # Keep this file simple — change model string if you later switch embeddings.
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
