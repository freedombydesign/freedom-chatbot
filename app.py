<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Chatbot with Voice</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f5f5f5;
      display: flex;
      height: 100vh;
      margin: 0;
    }
    .sidebar {
      width: 30%;
      background: #fff;
      border-right: 1px solid #ddd;
      display: flex;
      flex-direction: column;
      padding: 10px;
      overflow-y: auto;
    }
    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 20px;
    }
    .message {
      margin: 8px 0;
      padding: 10px;
      border-radius: 8px;
      max-width: 70%;
    }
    .user {
      background: #007bff;
      color: white;
      align-self: flex-end;
    }
    .bot {
      background: #e0e0e0;
      align-self: flex-start;
    }
    .input-container {
      display: flex;
      border-top: 1px solid #ddd;
      padding: 10px;
      background: #fff;
    }
    input[type="text"] {
      flex: 1;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    button {
      margin-left: 10px;
      padding: 10px 15px;
      border: none;
      border-radius: 4px;
      background: #007bff;
      color: white;
      cursor: pointer;
    }
    button:hover {
      background: #0056b3;
    }
    #micButton {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      border: none;
      background: #fff;
      cursor: pointer;
      margin-left: 10px;
      position: relative;
    }
    #micButton.recording::after {
      content: '';
      position: absolute;
      top: -10px;
      left: -10px;
      width: 70px;
      height: 70px;
      border-radius: 50%;
      border: 2px solid #007bff;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.9); opacity: 1; }
      100% { transform: scale(1.4); opacity: 0; }
    }
  </style>
</head>
<body>
  <div class="sidebar" id="chatSidebar"></div>
  <div class="chat-container">
    <div id="chatBox"></div>
    <div class="input-container">
      <input type="text" id="userInput" placeholder="Type a message...">
      <button onclick="sendMessage()">Send</button>
      <button id="micButton">🎤</button>
    </div>
  </div>

  <script>
    const chatBox = document.getElementById('chatBox');
    const chatSidebar = document.getElementById('chatSidebar');
    const micButton = document.getElementById('micButton');
    let mediaRecorder;
    let audioChunks = [];

    function addMessage(content, sender) {
      const msg = document.createElement('div');
      msg.className = `message ${sender}`;
      msg.textContent = content;
      chatBox.appendChild(msg);
      chatBox.scrollTop = chatBox.scrollHeight;

      const sidebarMsg = msg.cloneNode(true);
      chatSidebar.appendChild(sidebarMsg);
      chatSidebar.scrollTop = chatSidebar.scrollHeight;
    }

    async function sendMessage() {
      const input = document.getElementById('userInput');
      const userText = input.value;
      if (!userText) return;
      addMessage(userText, 'user');
      input.value = '';
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      });
      const data = await res.json();
      addMessage(data.reply, 'bot');
    }

    micButton.addEventListener('click', async () => {
      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        micButton.classList.add('recording');
        audioChunks = [];

        mediaRecorder.addEventListener('dataavailable', event => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener('stop', async () => {
          micButton.classList.remove('recording');
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('audio', audioBlob);
          const res = await fetch('/voice', { method: 'POST', body: formData });
          const data = await res.json();
          addMessage(data.reply, 'bot');
        });
      } else {
        mediaRecorder.stop();
      }
    });
  </script>
</body>
</html>
