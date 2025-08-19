<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chatbot</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f5f5f5;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .chat-container {
      width: 400px;
      height: 600px;
      background: white;
      display: flex;
      flex-direction: column;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .messages {
      flex: 1;
      padding: 15px;
      overflow-y: auto;
      border-bottom: 1px solid #ddd;
    }
    .message {
      margin: 8px 0;
      padding: 10px 14px;
      border-radius: 18px;
      max-width: 80%;
      word-wrap: break-word;
    }
    .message.user {
      background-color: #007bff;
      color: white;
      align-self: flex-end;
    }
    .message.bot {
      background-color: #e9ecef;
      color: black;
      align-self: flex-start;
    }
    .input-area {
      display: flex;
      align-items: center;
      padding: 10px;
    }
    .input-area input {
      flex: 1;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 20px;
      outline: none;
    }
    .send-btn {
      margin-left: 8px;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
    }
    .mic-btn {
      margin-left: 8px;
      background-color: white;
      border: 2px solid #007bff;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    .mic-btn.recording::after {
      content: '';
      position: absolute;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      border: 2px solid #007bff;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.9); opacity: 1; }
      100% { transform: scale(1.5); opacity: 0; }
    }
  </style>
</head>
<body>
  <div class="chat-container">
    <div class="messages" id="messages"></div>
    <div class="input-area">
      <input type="text" id="userInput" placeholder="Type a message..." />
      <button class="send-btn" onclick="sendMessage()">➤</button>
      <button class="mic-btn" id="micBtn">🎤</button>
    </div>
  </div>

  <script>
    const messagesEl = document.getElementById("messages");
    const userInput = document.getElementById("userInput");
    const micBtn = document.getElementById("micBtn");
    let isRecording = false;
    let recognition;

    function appendMessage(content, sender) {
      const msg = document.createElement("div");
      msg.classList.add("message", sender);
      msg.textContent = content;
      messagesEl.appendChild(msg);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    async function sendMessage() {
      const text = userInput.value.trim();
      if (!text) return;
      appendMessage(text, "user");
      userInput.value = "";

      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await response.json();
      if (data.reply) {
        appendMessage(data.reply, "bot");
      }
    }

    if ("webkitSpeechRecognition" in window) {
      recognition = new webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      micBtn.addEventListener("click", () => {
        if (!isRecording) {
          recognition.start();
          isRecording = true;
          micBtn.classList.add("recording");
        } else {
          recognition.stop();
          isRecording = false;
          micBtn.classList.remove("recording");
        }
      });

      recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        userInput.value = transcript;
      };
    }
  </script>
</body>
</html>
