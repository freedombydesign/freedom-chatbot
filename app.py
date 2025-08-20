from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests
from werkzeug.utils import secure_filename
import openai

app = Flask(__name__)
CORS(app)

# Config
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTS = {"pdf", "doc", "docx", "txt", "jpg", "jpeg", "png", "gif", "mp4", "mp3", "wav"}
conversations = {}

openai.api_key = os.getenv("OPENAI_API_KEY")
BING_KEY = os.getenv("BING_SEARCH_KEY")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

# System prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a warm, conversational AI assistant. "
        "Speak in a natural, human-like way, using casual, friendly expressions. "
        "Understand nuance, tone, and cultural context. "
        "Respond seamlessly in any language the user uses. "
        "Keep replies empathetic and approachable. "
        "Do not remind people you are an AI unless asked."
    )
}

# ---- ROUTER ----
def route_model(message):
    keywords = ["anxious", "therapy", "help", "practice", "struggling", "president", "today", "news"]
    if len(message) < 15 and not any(k in message.lower() for k in keywords):
        return "gpt-4o-mini"
    return "gpt-4.1"

# ---- CHAT ----
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    msg = data.get("message", "")

    if user_id not in conversations:
        conversations[user_id] = [SYSTEM_PROMPT]

    conversations[user_id].append({"role": "user", "content": msg})

    # Live search hook
    if any(k in msg.lower() for k in ["who is", "today", "date", "current", "latest", "president"]):
        try:
            r = requests.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers={"Ocp-Apim-Subscription-Key": BING_KEY},
                params={"q": msg, "mkt": "en-US"}
            )
            if r.status_code == 200:
                webdata = r.json()
                if "webPages" in webdata and "value" in webdata["webPages"]:
                    snippet = webdata["webPages"]["value"][0]["snippet"]
                    conversations[user_id].append({"role": "system", "content": f"Web search result: {snippet}"})
        except Exception as e:
            print("Search error:", e)

    # Pick model
    model = route_model(msg)

    resp = openai.chat.completions.create(
        model=model,
        messages=conversations[user_id],
        temperature=0.7,
    )

    reply = resp.choices[0].message.content
    conversations[user_id].append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

# ---- FILE UPLOAD ----
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)

    # Simple placeholder: In production, call OCR / Whisper / Vision here
    return jsonify({"status": "uploaded", "filename": file.filename})

if __name__ == "__main__":
    app.run(debug=True)
