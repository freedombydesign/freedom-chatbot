import express from "express";
import bodyParser from "body-parser";
import cors from "cors";

const app = express();
app.use(bodyParser.json());
app.use(cors());

// --- Example Chat Endpoint ---
app.post("/chat", (req, res) => {
  const { message, user_id } = req.body;

  // Here you’d plug in your GPT logic. For now it just echoes:
  res.json({
    reply: `👋 Hey${user_id ? " " + user_id : ""}, you said: "${message}"`
  });
});

// --- Health Check Endpoint (useful for Render) ---
app.get("/", (req, res) => {
  res.send("✅ Freedom Chatbot backend is running");
});

// --- IMPORTANT: use Render's PORT ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
