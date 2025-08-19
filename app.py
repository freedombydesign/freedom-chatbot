from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Use environment variable for your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # cost-effective + fast
        messages=[{"role": "user", "content": user_input}],
        max_tokens=500
    )

    return jsonify({"reply": response.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
@app.route("/", methods=["GET"])
def home():
    return "✅ Chatbot backend is running. Send POST requests to /chat."
