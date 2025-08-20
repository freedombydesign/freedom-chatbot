from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI()

# Store conversation history (use DB/Redis in production)
conversations = {}

# Hybrid router
def route_message(message: str):
    if len(message) < 15 and not any(
        word in message.lower()
        for word in ["anxious", "therapy", "help", "struggling", "practice", "explain"]
    ):
        return "gpt-4.1-mini"  # cheap, casual
    return "gpt-4.1"  # deeper reasoning & empathy

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message")
    uploaded_files = data.get("files", [])

    # Initialize user conversation
    if user_id not in conversations:
        conversations[user_id] = [
            {
                "role": "system",
                "content": (
                    "You are a warm, conversational AI assistant. "
                    "You use a natural, friendly tone, like a human. "
                    "You understand nuance, multiple languages, and can respond empathetically. "
                    "Keep answers engaging but not too long."
                ),
            }
        ]

    # Add user message
    conversations[user_id].append({"role": "user", "content": user_message})

    # Route to correct GPT model
    model_choice = route_message(user_message)

    # Call OpenAI
    completion = client.chat.completions.create(
        model=model_choice,
        messages=conversations[user_id],
        max_tokens=400,
        temperature=0.85,
    )

    reply = completion.choices[0].message["content"]

    # Add assistant reply to history
    conversations[user_id].append({"role": "assistant", "content": reply})

    return jsonify({"reply": reply})
