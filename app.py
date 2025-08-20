import os
from flask import Flask, request, jsonify
from openai import OpenAI
from supabase import create_client, Client

# -----------------------------
# Setup
# -----------------------------
app = Flask(__name__)

# OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Table name for memory
MEMORY_TABLE = "memory"


# -----------------------------
# Helpers
# -----------------------------
def save_message(user_id: str, role: str, content: str):
    """Save a message into Supabase memory table"""
    supabase.table(MEMORY_TABLE).insert({
        "user_id": user_id,
        "role": role,
        "content": content
    }).execute()


def get_user_memory(user_id: str):
    """Retrieve past messages for a user from Supabase"""
    response = supabase.table(MEMORY_TABLE).select("*").eq("user_id", user_id).order("id").execute()
    if response.data:
        return [{"role": msg["role"], "content": msg["content"]} for msg in response.data]
    return []


def choose_model(message: str) -> str:
    """Decide which model to use: gpt-4-mini for short, gpt-4.1 for long/deep"""
    if len(message.split()) < 30:  # short question → quick response
        return "gpt-4.1-mini"
    else:  # longer input → detailed reasoning
        return "gpt-4.1"


# -----------------------------
# Routes
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "anonymous")
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Fetch memory
    history = get_user_memory(user_id)

    # Add new user message to history
    history.append({"role": "user", "content": user_message})

    # Pick model
    model = choose_model(user_message)

    # Call OpenAI
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=history,
            max_tokens=500
        )

        reply = response.choices[0].message.content

        # Save both user and assistant messages to memory
        save_message(user_id, "user", user_message)
        save_message(user_id, "assistant", reply)

        return jsonify({"reply": reply, "model_used": model})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "ChatGPT Clone Backend is running 🚀"


# -----------------------------
# Run locally (for testing)
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
