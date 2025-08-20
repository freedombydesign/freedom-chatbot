from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

# Store conversation history per user (in memory for demo; use DB/Redis in production)
conversations = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

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
            }
        ]

    conversations[user_id].append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversations[user_id],
            max_tokens=500,
            temperature=0.85
        )

        reply = completion.choices[0].message.content
        conversations[user_id].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
