# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the function you already have in query_data.py
# query_rag(question: str) -> str
from query_data import query_rag

app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)


@app.route("/")
def index():
    # Serves static/frontend.html
    return app.send_static_file("frontend.html")


@app.route("/query", methods=["POST"])
def query_endpoint():
    payload = request.get_json(force=True)
    question = payload.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Call your RAG query function directly (no subprocess)
        answer = query_rag(question)
        return jsonify({"answer": answer})
    except Exception as e:
        # Return the error so you can debug in Firebase logs or locally
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
