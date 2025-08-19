from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os


app = Flask(__name__, static_folder=".")


# Ensure API key is present
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
raise RuntimeError("OPENAI_API_KEY env var is missing.")


client = OpenAI(api_key=OPENAI_API_KEY)


@app.route("/")
def serve_index():
# Serves index.html from the repo root
return send_from_directory(app.static_folder, "index.html")


@app.route("/healthz")
def healthz():
return {"status": "ok"}


@app.route("/chat", methods=["POST"])
def chat():
try:
data = request.get_json(silent=True) or {}
user_message = (data.get("message") or "").strip()
if not user_message:
return jsonify({"error": "Empty message."}), 400


# Call OpenAI (cheap + capable default model)
# You can swap to a different model if you prefer.
completion = client.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": user_message}],
temperature=0.7
)


reply = completion.choices[0].message.content
return jsonify({"reply": reply})


except Exception as e:
# In production, you might log this instead of returning raw errors.
return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
# Local dev: `python app.py` → http://localhost:5000
app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
