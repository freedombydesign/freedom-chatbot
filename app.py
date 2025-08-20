from flask import Flask, request, jsonify
conversations[user_id] = [
{"role": "system", "content": (
"You are a warm, conversational AI assistant. "
"Speak naturally, casually, and human-like. "
"Balance being concise with being engaging."
)}
]


# Add user message
conversations[user_id].append({"role": "user", "content": user_message})


# Inject web search if needed
if any(x in user_message.lower() for x in ["today", "latest", "current", "news", "president"]):
search_info = web_search(user_message)
if search_info:
conversations[user_id].append({"role": "system", "content": f"Web search says: {search_info}"})


# Call OpenAI
reply = openai.ChatCompletion.create(
model="gpt-4o-mini",
messages=conversations[user_id]
).choices[0].message["content"]


conversations[user_id].append({"role": "assistant", "content": reply})


return jsonify({"reply": reply})


# --- Voice Transcription ---
@app.route("/voice", methods=["POST"])
def voice():
audio = request.files["audio"]
transcript = openai.Audio.transcriptions.create(model="gpt-4o-transcribe", file=audio)
return jsonify({"transcript": transcript.text})


if __name__ == "__main__":
app.run(debug=True)
