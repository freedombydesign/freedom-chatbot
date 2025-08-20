from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Store conversation history
conversations = {}

# Environment variables (make sure to set these in Render or locally)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Real-time search using web API
def web_search(query):
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",  # Simple, free search API
            params={"q": query, "format": "json"}
        )
        data = response.json()
        if "AbstractText" in data and data["AbstractText"]:
            return data["AbstractText"]
        elif "RelatedTopics" in data and data["RelatedTopics"]:
            return data["RelatedTopics"][0].get("Text", "I couldn’t find anything relevant.")
        return "I couldn’t find anything relevant."
    except Exception as e:
        return f"Search error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")

    # Initialize conversation if new
    if user_id not in conversations:
        conversations[user_id] = [
            {
                "role": "system",
                "content": (
                    "You are a warm, conversational AI assistant. "
                    "Speak in a natural, human-like way, using casual, friendly expressions "
                    "when appropriate (like 'Hey, how’s it going?' or 'Got it, let’s fix that'). "
                    "You understand nuance, tone, and cultural context. "
                    "You can seamlessly respond in any language the user chooses. "
                    "Keep replies clear, empathetic, and approachable. "
                    "Do not remind people you are an AI unless they directly ask. "
                    "Balance being concise with being engaging."
                ),
            }
        ]

    # Add user message
    conversations[user_id].append({"role": "user", "content": user_message})

    # Web search hook for questions needing current info
    if any(word in user_message.lower() for word in ["date", "time", "president", "today"]):
        search_result = web_search(user_message)
        conversations[user_id].append({"role": "assistant", "content": search_result})
        return jsonify({"reply": search_result})

    # Fallback static reply (replace with OpenAI API if desired)
    reply = f"You said: {user_message}"
    conversations[user_id].append({"role": "assistant", "content": reply})

    return jsonify({"reply": reply})

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename
    # Save file temporarily (extend with video/audio/doc processing)
    filepath = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    return jsonify({"message": f"File {filename} uploaded successfully."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
