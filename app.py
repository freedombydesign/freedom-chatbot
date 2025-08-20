from flask import Flask, request, jsonify
import os
from openai import OpenAI

client = OpenAI()


app = Flask(__name__)

# Make sure you set your API key in Render's environment settings
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "<h1>Chatbot Backend Running ✅</h1><p>Send POST requests to /chat</p>", 200

@app.route("/health")
def health():
    return "ok", 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Call OpenAI API (ChatGPT-like behavior)
     response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": user_message}]
)

        )

        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render will provide PORT
    app.run(host="0.0.0.0", port=port)
