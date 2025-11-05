# query_data.py
import typing as t
import os
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

# Structured, Markdown-friendly prompt
PROMPT_TEMPLATE = """
You are an intelligent academic assistant. 
Answer based only on the following extracted context from trusted documents:

{context}

---

When replying, follow this exact structure using Markdown:

**Summary:**  
(A short 2–3 line overview of the main answer.)

**Detailed Explanation:**  
(A paragraph or two providing a well-structured explanation with reasoning.)

**Key Points:**  
- Use bullet points to highlight crucial facts or figures.
- Avoid redundancy.
- Stay concise and factual.

**References:**  
(If applicable, mention the source file names or relevant page numbers.)

Now answer the following question based on the above context:  
**{question}**
"""


def query_rag(query_text: str, model_name: str = "gemma3:12b") -> t.Tuple[str, t.List[dict]]:
    """
    Query the local Chroma DB for relevant document chunks,
    build a structured Markdown prompt, and query the selected local model.
    """
    # Load the embedding function and database
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Retrieve relevant chunks
    results = db.similarity_search_with_score(query_text, k=5)

    # Construct the context text for the prompt
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])

    # Prepare the chat-style prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Run the LLM with chosen model
    model = OllamaLLM(model=model_name)
    response_text = model.invoke(prompt)

    # Collect structured metadata for UI
    sources = []
    for doc, score in results:
        meta = doc.metadata or {}
        sources.append({
            "id": meta.get("id") or os.path.basename(meta.get("source", "unknown")),
            "source": os.path.basename(meta.get("source", "unknown")),
            "page": meta.get("page"),
            "score": float(score) if score is not None else None,
        })

    return response_text, sources


# For testing directly via CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="Question to query the RAG system.")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="LLM model name.")
    args = parser.parse_args()
    ans, srcs = query_rag(args.query_text, args.model)
    print("=== ANSWER ===\n", ans)
    print("\n=== SOURCES ===")
    for s in srcs:
        print(s)
