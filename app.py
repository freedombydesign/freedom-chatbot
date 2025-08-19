from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

@app.route("/chat", methods=["POST"])
def chat():
try:
data = request.get_json()
user_message = data.get("message", "")

response = client.chat.completions.create(
model="gpt-4o-mini", # or gpt-3.5-turbo if you want
messages=[{"role": "user", "content": user_message}]
)

bot_reply = response.choices[0].message.content
return jsonify({"reply": bot_reply})

except Exception as e:
return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
return "Chatbot is running! Send POST requests to /chat."

if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)




