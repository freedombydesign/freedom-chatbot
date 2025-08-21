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

// More diverse conversation starters
const CONVERSATION_STARTERS = [
  "Oof, 3 hours on emails? That's brutal.",
  "Email chaos is the worst kind of time drain.",
  "Been there! Email overwhelm is real.",
  "That's way too much time in your inbox.",
  "Classic email trap - super fixable though.",
  "Yikes, that's almost half a workday!",
  "Email prison is no joke.",
  "Drowning in emails? Let's fix this.",
  "Three hours?! We need to cut that in half.",
  "Email overload is a productivity killer."
];

// Random response types for dynamics
const RESPONSE_TYPES = [
  "diagnostic", // Ask questions to understand better
  "insight", // Give a quick observation
  "mixed" // Combine insight with questions
];

// Generate dynamic system prompt with more randomness
function generateSystemPrompt() {
  const starter = CONVERSATION_STARTERS[Math.floor(Math.random() * CONVERSATION_STARTERS.length)];
  const responseType = RESPONSE_TYPES[Math.floor(Math.random() * RESPONSE_TYPES.length)];
  const wordLimit = Math.floor(Math.random() * 30) + 35; // 35-65 words for tighter responses
  const timestamp = Date.now(); // Add timestamp to ensure uniqueness
  
  let behaviorInstructions = "";
  
  switch(responseType) {
    case "diagnostic":
      behaviorInstructions = "Ask 1-2 pointed questions to dig into the real problem.";
      break;
    case "insight":
      behaviorInstructions = "Give a quick reality check or observation, then see what they think.";
      break;
    case "mixed":
      behaviorInstructions = "Drop a quick insight AND ask what's really eating up their time.";
      break;
  }
  
  return `${timestamp}: You're a no-BS business strategist. React with: "${starter}" ${behaviorInstructions} Be conversational and direct. Under ${wordLimit} words. Don't sound like every other business coach - be genuine and varied in your approach.`;
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
