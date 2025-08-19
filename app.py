from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Root route (just to confirm app is running)
@app.route("/")
def home():
    return "Chatbot is running! Send POST requests to /chat."

# Set API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if available
        messages=[{"role": "user", "content": user_input}],
        max_tokens=150
    )

    return jsonify({"reply": response.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
