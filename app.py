from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Create memory folder if it doesn’t exist
MEMORY_FOLDER = "memory"
if not os.path.exists(MEMORY_FOLDER):
    os.makedirs(MEMORY_FOLDER)

def get_user_memory(user_id):
    filepath = os.path.join(MEMORY_FOLDER, f"{user_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {"history": []}

def save_user_memory(user_id, memory):
    filepath = os.path.join(MEMORY_FOLDER, f"{user_id}.json")
    with open(filepath, "w") as f:
        json.dump(memory, f)

@app.route("/", methods=["GET"])
def home():
    return "✅ Freedom Chatbot is running!"

@app.route("/chat", methods=["POST"])
def chat():
    # Parse JSON body safely
    data = request.get_json()
    if not data or "user_id" not in data or "message" not in data:
        return jsonify({"error": "Invalid request. Must include user_id and message."}), 400

    user_id = data["user_id"]
    message = data["message"]

    # Load user memory
    memory = get_user_memory(user_id)

    # Save conversation
    memory["history"].append({"user": message})

    # Here is where you’d normally plug in your AI logic
    bot_reply = f"You said: {message}"

    # Save bot reply to memory
    memory["history"].append({"bot": bot_reply})
    save_user_memory(user_id, memory)

    return jsonify({"reply": bot_reply, "memory": memory})

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000)
