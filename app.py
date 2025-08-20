from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Use a real search API (SerpAPI, Bing, or Tavily)
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_ENGINE_URL = "https://api.tavily.com/search"  # Example: Tavily

conversations = {}
user_names = {}


def web_search(query):
    try:
        resp = requests.post(
            SEARCH_ENGINE_URL,
            json={"api_key": SEARCH_API_KEY, "query": query, "max_results": 3},
            timeout=10
        )
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            snippets = [r.get("content", r.get("title", "")) for r in data["results"]]
            return "\n".join(snippets[:3])
        return "Sorry, I couldn’t find anything reliable just now."
    except Exception as e:
        return f"Search error: {e}"


@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.remote_addr
    msg = request.form.get("message", "")

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
                    "Speak in a natural, human-like way. "
                    f"Use the user’s first name ({user_names[user_id]}) to personalize replies."
                )
            }]
            return jsonify({"reply": f"Great to meet you, {user_names[user_id]}! What can I do for you today?"})

    # Initialize if missing
    if user_id not in conversations:
        conversations[user_id] = [{
            "role": "system",
            "content": "You are a warm, conversational AI assistant."
        }]

    conversations[user_id].append({"role": "user", "content": msg})

    # Routing: search vs model
    if any(w in msg.lower() for w in ["today", "latest", "current", "news", "president"]):
        search_result = web_search(msg)
        reply = f"Here’s what I found:\n{search_result}"
    else:
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=conversations[user_id]
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
