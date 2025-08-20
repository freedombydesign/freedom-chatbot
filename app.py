from flask import Flask, request, jsonify
from openai import OpenAI
import os
from memory import save_user, get_user, save_message, get_messages

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default_user")
    message = data.get("message")

    # Ensure user exists in Supabase
    save_user(user_id)

    # Save the incoming user message
    save_message(user_id, "user", message)

    # Retrieve last 10 messages from history
    history = get_messages(user_id)

    # Format history into OpenAI-compatible messages
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

    # Generate AI response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    ai_message = response.choices[0].message.content

    # Save AI response
    save_message(user_id, "assistant", ai_message)

    return jsonify({"reply": ai_message})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
