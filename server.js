import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import OpenAI from "openai";
import { createClient } from "@supabase/supabase-js";

const app = express();
app.use(bodyParser.json());
app.use(cors());

// ✅ Environment variables
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

// 🔹 Chat route
app.post("/chat", async (req, res) => {
  try {
    const { user_id, message } = req.body;

    // 1. Get model reply first
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",   // Fixed model name - should be gpt-4o-mini, not gpt-4.1-mini
      messages: [{ role: "user", content: message }]
    });
    
    const botReply = completion.choices[0].message.content;

    // 2. Save both user message and bot response in ONE insert to conversations table
    const { data, error } = await supabase
      .from("Conversations")  // Changed from "memory" to "conversations"
      .insert([{ 
        user_id: user_id, 
        message: message,     // User's message
        response: botReply    // AI's response
      }]);

    if (error) {
      console.error("Supabase error:", error);
      return res.status(500).json({ error: error.message });
    }

    // 3. Return reply
    res.json({ reply: botReply });

  } catch (err) {
    console.error("Error in /chat route:", err);
    res.status(500).json({ error: err.message });
  }
});

// ✅ Health check route
app.get("/", (req, res) => {
  res.json({ status: "AI Strategist API is running!" });
});

// ✅ Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
