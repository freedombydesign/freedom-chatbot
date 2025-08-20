## ✅ Fixed Backend (Flask, `app.py`)
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


# Real search (Tavily or Bing)
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_URL = "https://api.tavily.com/search"


conversations, user_names = {}, {}


# Web search


def web_search(query):
try:
resp = requests.get(SEARCH_URL, params={"query": query, "max_results": 3}, headers={"Authorization": f"Bearer {SEARCH_API_KEY}"})
data = resp.json()
if "results" in data and data["results"]:
return data["results"][0]["content"]
return "Sorry, I couldn’t find anything reliable just now."
except Exception as e:
return f"Search error: {e}"


@app.route("/chat", methods=["POST"])
def chat():
user_id = request.remote_addr
user_msg = request.form.get("message", "")


if user_id not in user_names:
return jsonify({"reply": "👋 Hey! Before we get started, what’s your first name?"})


if user_id not in conversations:
conversations[user_id] = [
{"role": "system", "content": "You are a warm, conversational AI assistant."}
]


conversations[user_id].append({"role": "user", "content": user_msg})


# If greeting, set name
if "my name is" in user_msg.lower():
name = user_msg.split("is")[-1].strip().split()[0]
user_names[user_id] = name.capitalize()
return jsonify({"reply": f"Great to meet you, {name.capitalize()}! What can I do for you today?"})


# If query requires live info
if any(word in user_msg.lower() for word in ["today", "latest", "news", "president"]):
info = web_search(user_msg)
conversations[user_id].append({"role": "assistant", "content": info})
return jsonify({"reply": info})


# Otherwise, use OpenAI
reply = openai.chat.completions.create(
model="gpt-4o-mini",
messages=conversations[user_id]
)
msg = reply.choices[0].message["content"]
conversations[user_id].append({"role": "assistant", "content": msg})
return jsonify({"reply": msg})


@app.route("/upload", methods=["POST"])
def upload():
file = request.files["file"]
path = os.path.join("uploads", file.filename)
os.makedirs("uploads", exist_ok=True)
file.save(path)
return jsonify({"url": f"/uploads/{file.filename}"})


if __name__ == "__main__":
app.run(debug=True)
```
