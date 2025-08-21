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
// Replace just the SYSTEM_PROMPT with this more restrictive version:

const SYSTEM_PROMPT = "You are a business strategist. CRITICAL RULE: Never give solutions immediately. Always start by asking 2-3 specific diagnostic questions to understand their exact situation. Only after they answer your questions should you give focused advice. Keep all responses under 100 words. Always end by asking what they want to explore next. Be conversational and engaging, like a trusted advisor who listens first.";

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
