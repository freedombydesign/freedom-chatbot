from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔹 Hybrid Routing Logic
def route_message(message: str) -> str:
    """Route message to GPT-4-mini or GPT-4.1 based on complexity"""
    if len(message) < 15 and not any(
        word in message.lower() for word in ["anxious", "therapy", "help", "struggling", "practice"]
    ):
        return "gpt-4.1-mini"
    return "gpt-4.1"

# 🔹 Web Search Fallback
def web_search(query: str) -> str:
    """Quick web search using DuckDuckGo API"""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json"},
            timeout=5
        )
        data = resp.json()
        if "AbstractText" in data and data["AbstractText"]:
            return data["AbstractText"]
        elif "RelatedTopics" in data and len(data["RelatedTopics"]) > 0:
            return data["RelatedTopics"][0].get("Text", "No summary available.")
        return "Sorry, I couldn’t find anything on that."
    except Exception as e:
        return f"Search error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    files = request.files.getlist("files")

    # Handle uploads (basic)
    file_summaries = []
    for f in files:
        file_summaries.append(f"📎 {f.filename} uploaded (size: {len(f.read())} bytes)")
        f.seek(0)

    # Special case → Web search if question looks factual/current
    if any(keyword in user_msg.lower() for keyword in ["today", "date", "time", "news", "weather"]):
        search_result = web_search(user_msg)
        return jsonify({"reply": f"🌐 {search_result}"})

    # Hybrid model routing
    model = route_message(user_msg)

    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a warm, conversational AI assistant. Be supportive, natural, and nuanced. Understand all languages."
            },
            {"role": "user", "content": user_msg},
        ]
    )

    reply = completion["choices"][0]["message"]["content"]

    if file_summaries:
        reply += "\n\n" + "\n".join(file_summaries)

    return jsonify({"reply": reply})

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
                )

if __name__ == "__main__":
    app.run(debug=True)
