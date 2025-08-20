<!DOCTYPE html>
<div id="chatbox">
<div id="messages"></div>
<div id="inputArea">
<input type="text" id="message" placeholder="Ask me anything..." />
<button id="micBtn">🎤</button>
<label for="fileInput" id="fileBtn">📎</label>
<input type="file" id="fileInput" multiple />
<button id="sendBtn">➤</button>
</div>
</div>


<script>
const messagesDiv = document.getElementById("messages");
const input = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const fileInput = document.getElementById("fileInput");


let recognition;
let isRecording = false;


// --- Display Messages ---
function addMessage(text, sender) {
const div = document.createElement("div");
div.className = `msg ${sender}`;
div.textContent = text;
messagesDiv.appendChild(div);
messagesDiv.scrollTop = messagesDiv.scrollHeight;
}


// --- Send Message ---
async function sendMessage() {
const text = input.value.trim();
if (!text) return;
addMessage(text, "user");
input.value = "";


const res = await fetch("http://127.0.0.1:5000/chat", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ user_id: "demo", message: text })
});
const data = await res.json();
addMessage(data.response, "assistant");
}


sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", e => { if (e.key === "Enter") sendMessage(); });


// --- File Upload ---
fileInput.addEventListener("change", async () => {
for (const file of fileInput.files) {
const formData = new FormData();
formData.append("file", file);
const res = await fetch("http://127.0.0.1:5000/upload", { method: "POST", body: formData });
const data = await res.json();
if (data.success) addMessage(`Uploaded: ${data.filename}`, "assistant");
}
});


// --- Voice Recognition ---
if ('webkitSpeechRecognition' in window) {
recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;


recognition.onresult = (event) => {
let transcript = "";
for (let i = event.resultIndex; i < event.results.length; i++) {
transcript += event.results[i][0].transcript;
}
input.value = transcript;
};


recognition.onend = () => { isRecording = false; micBtn.textContent = "🎤"; };
}


micBtn.addEventListener("click", () => {
if (isRecording) {
recognition.stop();
isRecording = false;
micBtn.textContent = "🎤";
} else {
recognition.start();
isRecording = true;
micBtn.textContent = "⏹";
}
});
</script>
</body>
</html>
