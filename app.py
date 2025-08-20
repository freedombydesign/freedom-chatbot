from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversations = {}
user_names = {}

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.remote_addr
    msg = request.form.get("message", "")
    files = request.files.getlist("files")

    # Ask name if not set
    if user_id not in user_names:
        if not msg.strip():
            return jsonify({"reply": "Hi! Before we get started, what’s your first name?"})
        else:
            user_names[user_id] = msg.strip().split()[0]
            conversations[user_id] = [{
                "role": "system",
                "content": (
                    "You are a warm, conversational AI assistant. "
                    "Speak in a natural, human-like way, using casual, friendly expressions. "
                    "You can respond in any language. "
                    "Use the user’s first name (" + user_names[user_id] + ") to personalize replies."
                )
            }]
            return jsonify({"reply": f"Great to meet you, {user_names[user_id]}! What can I do for you today?"})

    # Initialize conversation
    if user_id not in conversations:
        conversations[user_id] = [{
            "role": "system",
            "content": (
                "You are a warm, conversational AI assistant. "
                "Speak naturally, empathetically, and be engaging."
            )
        }]

    conversations[user_id].append({"role": "user", "content": msg})

    # Hybrid model routing
    def route_message(message):
        if len(message) < 15 and not any(word in message.lower() 
            for word in ["anxious", "help", "therapy", "practice", "struggling"]):
            return "gpt-4.1-mini"
        return "gpt-4.1"

    model = route_message(msg)

    # If user explicitly asks for real-time info
    if any(w in msg.lower() for w in ["today", "latest", "current", "news", "president"]):
        # Web search fallback (pseudo — replace with your real search API)
        reply = "Let me quickly check the latest info for you..."
    else:
        completion = client.chat.completions.create(
            model=model,
            messages=conversations[user_id],
        )
        reply = completion.choices[0].message.content

    conversations[user_id].append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

@app.route("/voice", methods=["POST"])
def voice():
    audio = request.files["audio"]
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=audio
    )
    return jsonify({"transcript": transcript.text})

if __name__ == "__main__":
    app.run(debug=True)
