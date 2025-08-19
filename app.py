from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

# Conversation memory storage (in-memory for now)
conversation_history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Save user message to conversation history
        conversation_history.append({"role": "user", "content": user_message})

        # Limit memory (e.g., last 20 messages)
        if len(conversation_history) > 20:
            conversation_history.pop(0)

        # Create response with context
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."}] + conversation_history
        )

        reply = response.choices[0].message.content

        # Save assistant reply in memory
        conversation_history.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply, "history": conversation_history})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
