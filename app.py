from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from supabase import create_client, Client

# --- Setup ---
app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Supabase setup
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# --- Chat Route ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    username = data.get("username", "User")
    message = data.get("message")

    if not message:
        return jsonify({"reply": "No message provided."}), 400

    # Store user message in Supabase memory
    supabase.table("memory").insert({
        "user_id": user_id,
        "role": "user",
        "content": message
    }).execute()

    # Fetch conversation history for this user
    history = supabase.table("memory").select("*").eq("user_id", user_id).order("id").execute()
    messages = [{"role": row["role"], "content": row["content"]} for row in history.data]

    # Add system prompt
    messages.insert(0, {"role": "system", "content": f"You are a helpful AI assistant talking to {username}."})

    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",  # you can swap between "gpt-4.1-mini" and "gpt-4.1"
        messages=messages
    )

    reply = response["choices"][0]["message"]["content"]

    # Store AI reply in Supabase memory
    supabase.table("memory").insert({
        "user_id": user_id,
        "role": "assistant",
        "content": reply
    }).execute()

    return jsonify({"reply": reply})


# --- File Upload Route ---
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = file.filename
    upload_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(upload_path)
    return jsonify({"filename": filename})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
