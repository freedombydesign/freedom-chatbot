from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import datetime

app = Flask(__name__)
CORS(app)

openai.api_key = "YOUR_OPENAI_API_KEY"

conversations = {}

# --------------------------
# HELPER: Route message
# --------------------------
def route_message(message):
    keywords = ["anxious", "help", "therapy", "practice", "struggling", "explain"]
    if len(message) < 15 and not any(word in message.lower() for word in keywords):
        return "gpt-4o-mini"
    return "gpt-4.1"

# --------------------------
# HELPER: Web Search
# --------------------------
def perform_web_search(query):
    if "date" in query.lower() or "time" in query.lower():
        return f"The current date and time is {datetime.datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}."
    
    try:
        res = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1},
            timeout=5
        )
        data = res.json()
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            return data["RelatedTopics"][0].get("Text", "I couldn’t find anything useful.")
        return "I couldn’t find any good info on that."
    except Exception:
        return "Sorry, I had trouble reaching the web."

# --------------------------
# ROUTE: Chat
# --------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.json.get("user_id", "default")
    message = request.json.get("message", "")

    # Initialize conversation if new
    if user_id not in conversations:
        conversations[user_id] = [
            {
                "role": "system",
                "content": (
                    "You are a warm, conversational AI assistant. "
                    "Speak in a natural, human-like way, using casual, friendly expressions "
                    "when appropriate. You understand nuance, tone, and cultural context. "
                    "Keep replies clear, empathetic, and approachable. "
                    "Do not remind people you are an AI unless asked directly. "
                    "Balance being concise with being engaging."
                )
            }
        ]

    # Append user message
    conversations[user_id].append({"role": "user", "content": message})

    # Try web search if needed
    if "who is the president" in message.lower() or "current" in message.lower():
        web_answer = perform_web_search(message)
        conversations[user_id].append({"role": "assistant", "content": web_answer})
        return jsonify({"reply": web_answer})

    # Decide which model to use
    model = route_message(message)

    # Get AI response
    response = openai.chat.completions.create(
        model=model,
        messages=conversations[user_id],
    )
    reply = response.choices[0].message["content"]

    conversations[user_id].append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

# --------------------------
# ROUTE: File Upload
# --------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename
    # TODO: integrate doc/image/video analysis here
    return jsonify({"message": f"Received {filename}, but file analysis not fully wired yet."})

if __name__ == "__main__":
    app.run(debug=True)
