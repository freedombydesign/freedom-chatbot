const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());

// Replace this with your actual bot logic
function getBotReply(message) {
  return `Echo: ${message}`;
}

app.post("/chat", (req, res) => {
  const { message, user_id } = req.body;

  if (!message || !user_id) {
    return res.status(400).json({ error: "Missing message or user_id" });
  }

  const botReply = getBotReply(message);
  res.json({ reply: botReply }); // Important: send JSON back to frontend
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
