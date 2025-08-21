// Enhanced server.js with randomness and personality
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

// Random conversation starters for variety
const CONVERSATION_STARTERS = [
  "Ah, I see what's happening here.",
  "That's a classic founder bottleneck!",
  "Okay, let me think about this...",
  "Hmm, interesting situation.",
  "I've seen this pattern before.",
  "That sounds frustrating!",
  "Yep, totally get it.",
  "Oh, this is solvable for sure."
];

// Random response types for dynamics
const RESPONSE_TYPES = [
  "diagnostic", // Ask questions to understand better
  "insight", // Give a quick observation
  "mixed" // Combine insight with questions
];

// Generate dynamic system prompt with randomness
function generateSystemPrompt() {
  const starter = CONVERSATION_STARTERS[Math.floor(Math.random() * CONVERSATION_STARTERS.length)];
  const responseType = RESPONSE_TYPES[Math.floor(Math.random() * RESPONSE_TYPES.length)];
  const wordLimit = Math.floor(Math.random() * 40) + 40; // 40-80 words
  
  let behaviorInstructions = "";
  
  switch(responseType) {
    case "diagnostic":
      behaviorInstructions = "Focus on asking 1-2 smart questions to understand their situation better.";
      break;
    case "insight":
      behaviorInstructions = "Give a quick insight or observation, then ask what they want to tackle.";
      break;
    case "mixed":
      behaviorInstructions = "Share a brief insight AND ask a follow-up question.";
      break;
  }
  
  return `You're a business strategist helping founders remove bottlenecks. Start your response with something like "${starter}" but make it natural. ${behaviorInstructions} Talk like a smart friend - casual, direct, no corporate speak. Keep it under ${wordLimit} words. Vary your style each time. Sometimes be more analytical, sometimes more encouraging, sometimes more direct.`;
}

app.post("/chat", async (req, res) => {
  try {
    const { user_id, message } = req.body;

    // Get conversation history
    const { data: history } = await supabase
      .from("memory")
      .select("message, response")
      .eq("user_id", user_id)
      .order("created_at", { ascending: true })
      .limit(10);

    // Generate a fresh, random system prompt for each conversation
    const dynamicPrompt = generateSystemPrompt();

    // Build conversation context with random temperature
    const randomTemperature = 0.6 + (Math.random() * 0.4); // 0.6 to 1.0 for variety
    
    const messages = [{ role: "system", content: dynamicPrompt }];
    
    // Add conversation history
    if (history && history.length > 0) {
      history.forEach(conv => {
        messages.push({ role: "user", content: conv.message });
        messages.push({ role: "assistant", content: conv.response });
      });
    }
    
    messages.push({ role: "user", content: message });

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: messages,
      temperature: randomTemperature, // Dynamic temperature
      max_tokens: 200, // Slightly more room for variety
      presence_penalty: 0.3, // Encourage new topics/words
      frequency_penalty: 0.3 // Reduce repetitive phrases
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
  res.json({ status: "Dynamic AI Strategist is running!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
