// Enhanced server.js with conversational AI prompt
import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import OpenAI from "openai";
import { createClient } from "@supabase/supabase-js";

const app = express();
app.use(bodyParser.json());
app.use(cors());

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

// Enhanced conversational system prompt
const SYSTEM_PROMPT = "You are the AI Strategist for the Freedom by Design Method, helping service-based founders remove themselves as bottlenecks in their business. Be conversational and engaging, not formal or robotic. Ask 2-3 specific questions to understand their situation before giving advice. Give ONE focused insight or strategy per response, not everything at once. Always end with asking what would be most helpful to explore next. Keep responses under 150 words unless specifically asked for detailed steps.";

app.post("/chat", async (req, res) => {
  try {
    const { user_id, message } = req.body;

    // Get conversation history from database
    const { data: history } = await supabase
      .from("memory")
      .select("message, response")
      .eq("user_id", user_id)
      .order("created_at", { ascending: true })
      .limit(10);

    // Build conversation context
    const messages = [{ role: "system", content: SYSTEM_PROMPT }];
    
    // Add conversation history
    if (history && history.length > 0) {
      history.forEach(conv => {
        messages.push({ role: "user", content: conv.message });
        messages.push({ role: "assistant", content: conv.response });
      });
    }
    
    // Add current message
    messages.push({ role: "user", content: message });

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: messages,
      temperature: 0.7,
      max_tokens: 300
    });
    
    const botReply = completion.choices[0].message.content;

    // Save to database
    const { data, error } = await supabase
      .from("memory")
      .insert([{ 
        user_id: user_id, 
        message: message,
        response: botReply
      }]);

    if (error) {
      console.error("Supabase error:", error);
      return res.status(500).json({ error: error.message });
    }

    res.json({ reply: botReply });

  } catch (err) {
    console.error("Error in /chat route:", err);
    res.status(500).json({ error: err.message });
  }
});

app.get("/", (req, res) => {
  res.json({ status: "Conversational AI Strategist is running!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
