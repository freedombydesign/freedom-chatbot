import express from "express";
import cors from "cors";
import { createClient } from "@supabase/supabase-js";
import OpenAI from "openai";

const app = express();
app.use(cors());
app.use(express.json());

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

app.post("/chat", async (req, res) => {
  try {
    const { user_id, message } = req.body;

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You're Ruth's AI strategist. Be helpful and conversational. For new users, introduce yourself: 'Hi there! I'm your AI strategist, built on the Freedom by Design Method. What's your name?'" },
        { role: "user", content: message }
      ],
      temperature: 0.7,
      max_tokens: 200
    });

    const reply = completion.choices[0].message.content;

    await supabase.from("memory").insert([{ 
      user_id, 
      message,
      response: reply
    }]);

    res.json({ reply });

  } catch (err) {
    console.error("Error:", err);
    res.status(500).json({ error: err.message });
  }
});

app.get("/", (req, res) => {
  res.json({ status: "Simple AI Strategist Running!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on ${PORT}`));
