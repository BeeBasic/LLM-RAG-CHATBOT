# app.py
import os
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from query_data import query_rag

# === Constants ===
CHROMA_PATH = "chroma"
DATA_PATH = os.path.join(os.getcwd(), "data")
AVAILABLE_MODELS = [
    "deepseek-coder-v2:latest",
    "codegemma:latest",
    "mistral:7b-instruct",
    "gemma3:12b",
]

# === App setup ===
app = Flask(__name__)
CORS(app)  # Allow React frontend (5173) to talk to Flask (5000)


# === Routes ===

@app.route("/models", methods=["GET"])
def models_endpoint():
    """Expose available LLM model names to the frontend."""
    return jsonify({"models": AVAILABLE_MODELS})


@app.route("/query", methods=["POST"])
def query_endpoint():
    """
    Handle RAG model queries.

    Request JSON:
    {
        "question": "What is RAG?",
        "model": "gemma3:12b"
    }
    Response JSON:
    {
        "answer": "...",
        "sources": [
            {"source": "MID-2024-25.pdf", "page": 3, "score": 0.87},
            ...
        ]
    }
    """
    payload = request.get_json(force=True, silent=True) or {}
    question = (payload.get("question") or "").strip()
    model_name = (payload.get("model") or "gemma3:12b").strip()

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        answer_text, sources = query_rag(question, model_name)
        return jsonify({"answer": answer_text, "sources": sources})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/<path:filename>", methods=["GET"])
def serve_file(filename):
    """
    Serve PDF files from /data for download.
    Cross-platform safe (handles Windows-style paths).
    """
    clean_name = filename.replace("\\", "/").split("/")[-1]
    file_path = os.path.join(DATA_PATH, clean_name)

    if not os.path.isfile(file_path):
        abort(404, description=f"File not found: {clean_name}")

    return send_from_directory(
        DATA_PATH,
        clean_name,
        as_attachment=True,
        download_name=clean_name,
        mimetype="application/pdf",
    )


@app.route("/performance", methods=["GET"])
def performance():
    """Return mock performance metrics for frontend graphs."""
    data = {
        "model": "gemma3:12b",
        "embedding": "nomic-embed-text",
        "metrics": {
            "accuracy": [0.72, 0.78, 0.81, 0.84, 0.88],
            "loss": [0.9, 0.7, 0.55, 0.4, 0.32],
        },
        "confusion_matrix": [
            [85, 5, 10],
            [4, 90, 6],
            [7, 3, 90],
        ],
        "labels": ["Correct", "Minor Error", "Major Error"],
    }
    return jsonify(data)


# === Run app ===
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
