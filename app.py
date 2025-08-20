from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ✅ Store conversations per user (simple memory)
conversations = {}

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.json.get("user", "default")
    message = request.json.get("message")

    if user_id not in conversations:
        conversations[user_id] = []

    conversations[user_id].append({"role": "user", "content": message})

    # Example response (replace with AI call)
    response = {"reply": f"Echo: {message}"}

    conversations[user_id].append({"role": "assistant", "content": response["reply"]})

    return jsonify(response)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filepath = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)
    return jsonify({"status": "success", "filename": file.filename})

if __name__ == "__main__":
    # ✅ IMPORTANT FIX: Bind to 0.0.0.0 and use PORT from Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
