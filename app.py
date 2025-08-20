from flask import Flask, request, jsonify
if len(message) < 15 and not any(
word in message.lower() for word in ["help", "anxious", "therapy", "practice", "struggling"]
):
model = "gpt-4.1-mini"
else:
model = "gpt-4.1"


# --- Web Search Hook ---
if "date" in message.lower() or "time" in message.lower() or "president" in message.lower():
try:
search = requests.get(
"https://api.duckduckgo.com/",
params={"q": message, "format": "json"},
timeout=10,
)
data = search.json()
if data.get("AbstractText"):
answer = data["AbstractText"]
else:
answer = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')}"
conversations[user_id].append({"role": "assistant", "content": answer})
return jsonify({"response": answer})
except Exception as e:
print("Web search error:", e)


# --- Fallback OpenAI (Pseudo-call, replace with real OpenAI SDK) ---
reply = f"(Simulated {model} reply) You said: {message}"
conversations[user_id].append({"role": "assistant", "content": reply})


return jsonify({"response": reply})


# --- Route: File Upload ---
@app.route("/upload", methods=["POST"])
def upload_file():
if "file" not in request.files:
return jsonify({"error": "No file part"}), 400
file = request.files["file"]
if file.filename == "":
return jsonify({"error": "No file selected"}), 400
if file and allowed_file(file.filename):
filename = secure_filename(file.filename)
filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
file.save(filepath)
return jsonify({"success": True, "filename": filename})
return jsonify({"error": "File type not allowed"}), 400


if __name__ == "__main__":
app.run(debug=True)
