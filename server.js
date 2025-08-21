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

    // 1. Save user message
    await supabase
      .from("memory")
      .insert([{ user_id, message }]);

    // 2. Get model reply
    const completion = await openai.chat.completions.create({
      model: "gpt-4.1-mini",   // ✅ Cheapest GPT-4.1 option
      messages: [{ role: "user", content: message }]
    });

    const botReply = completion.choices[0].message.content;

    // 3. Save bot reply
    await supabase
      .from("memory")
      .insert([{ user_id, response: botReply }]);

    // 4. Return reply
    res.json({ reply: botReply });

  } catch (err) {
    console.error("Error in /chat route:", err);
    res.status(500).json({ error: err.message });
  }
});

// ✅ Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
