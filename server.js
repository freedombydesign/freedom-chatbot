// Complete AI Strategist - EXACT match to your environment
import express from "express";
import multer from "multer";
import cors from "cors";
import { createClient } from "@supabase/supabase-js";
import OpenAI from "openai";
import Airtable from "airtable";
import fs from "fs";
import path from "path";

const app = express();
const upload = multer({ dest: "uploads/" });
app.use(cors());
app.use(express.json());

// ====== ENV VARS - EXACT MATCH TO YOUR RENDER SETUP ======
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;  // matches your env var
const AIRTABLE_API_KEY = process.env.AIRTABLE_KEY;        // matches your env var
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE;       // matches your env var
const MODEL = process.env.MODEL || "gpt-4o-mini";

// ====== CLIENTS ======
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
const airtable = new Airtable({ apiKey: AIRTABLE_API_KEY }).base(AIRTABLE_BASE_ID);

// ====== DYNAMIC PERSONALITY SYSTEM ======
const CONVERSATION_STARTERS = [
  "Oof, that sounds like a real challenge.",
  "Email chaos is the worst kind of time drain.",
  "Been there! Business overwhelm is real.",
  "That's way too much on your plate.",
  "Classic founder trap - super fixable though.",
  "Yikes, that's eating up serious time!",
  "Bottleneck alert! Let's fix this.",
  "Drowning in tasks? Let's get you unstuck.",
  "That's a productivity killer for sure.",
  "Time to remove yourself from that chaos."
];

const RESPONSE_TYPES = ["diagnostic", "insight", "mixed"];

// Extract name from conversation history - MATCHES YOUR DB STRUCTURE
function extractNameFromHistory(history) {
  for (let conv of history) {
    // Look in the message column (your DB structure)
    const nameMatch = conv.message.match(/(?:i'm|i am|my name is|call me)\s+([a-zA-Z]+)/i);
    if (nameMatch) {
      return nameMatch[1];
    }
  }
  return null;
}

// Generate dynamic system prompt
function generateSystemPrompt(userName = null, isNewUser = false) {
  if (isNewUser) {
    return "You're Ruth's AI strategist built on the Freedom by Design Method. Introduce yourself with exactly: 'Hi there! I'm your AI strategist, built on the Freedom by Design Method. I'll guide you step-by-step so you can focus on growth while your business runs with less of you. Let's start simple—what's your name?' Be warm and welcoming.";
  }

  const starter = CONVERSATION_STARTERS[Math.floor(Math.random() * CONVERSATION_STARTERS.length)];
  const responseType = RESPONSE_TYPES[Math.floor(Math.random() * RESPONSE_TYPES.length)];
  const wordLimit = Math.floor(Math.random() * 30) + 35;
  const timestamp = Date.now();
  
  let behaviorInstructions = "";
  let nameInstruction = userName ? `Use their name "${userName}" occasionally in conversation to be personal. ` : "";
  
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
  
  return `${timestamp}: You're Ruth's AI strategist using the Freedom by Design Method. ${nameInstruction}React with: "${starter}" ${behaviorInstructions} Be conversational and direct. Under ${wordLimit} words. Help founders remove themselves as bottlenecks.`;
}

// ====== MEMORY SYSTEM - MATCHES YOUR DB EXACTLY ======
async function getMemory(user_id) {
  const { data } = await supabase
    .from("memory")
    .select("message, response")
    .eq("user_id", user_id)
    .order("created_at", { ascending: true })
    .limit(20);
  return data || [];
}

// ====== SEMANTIC SEARCH - MATCHES YOUR AIRTABLE ENV VARS ======
async function semanticSearch(query) {
  try {
    // Try to search your Airtable - adjust table name as needed
    const records = await airtable("Frameworks").select({
      filterByFormula: `SEARCH("${query}", {Title}) > 0`
    }).firstPage();
    return records.map((r) => r.fields);
  } catch (error) {
    console.error("Airtable search error:", error);
    return [];
  }
}

// ====== MAIN CHAT API - MATCHES YOUR CURRENT WORKING STRUCTURE ======
app.post("/chat", async (req, res) => {
  try {
    const { user_id, message } = req.body;
    
    // Get conversation history using YOUR database structure
    let history = await getMemory(user_id);
    const isNewUser = !history || history.length === 0;
    
    // Extract user name from history
    const userName = extractNameFromHistory(history);
    
    // Search Airtable for relevant frameworks (if available)
    let frameworks = [];
    try {
      frameworks = await semanticSearch(message);
    } catch (airtableError) {
      console.log("Airtable not available, continuing without frameworks");
    }
    
    let frameworkContext = "";
    if (frameworks.length > 0) {
      frameworkContext = `\n\nRelevant frameworks: ${frameworks.map(f => f.Title || f.Name).join(", ")}`;
    }

    // Generate dynamic system prompt
    const systemPrompt = generateSystemPrompt(userName, isNewUser);

    // Build messages for OpenAI using YOUR database structure
    const messages = [
      { role: "system", content: systemPrompt + frameworkContext },
      ...history.map((m) => [
        { role: "user", content: m.message },
        { role: "assistant", content: m.response }
      ]).flat(),
      { role: "user", content: message }
    ];

    // Query OpenAI with random temperature for personality
    const randomTemperature = 0.6 + (Math.random() * 0.4);
    
    const completion = await openai.chat.completions.create({
      model: MODEL,
      messages,
      temperature: randomTemperature,
      max_tokens: 300,
      presence_penalty: 0.3,
      frequency_penalty: 0.3
    });

    const botReply = completion.choices[0].message.content;

    // Save to YOUR database structure
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
    console.error("Chat error:", err);
    res.status(500).json({ error: err.message });
  }
});

// ====== ADVANCED FILE UPLOAD API (for future use) ======
app.post("/api/chat", upload.array("files"), async (req, res) => {
  // This is the advanced version with file upload
  // Same logic as above but with file processing
  // We can enable this later when you're ready for files
  res.json({ message: "Advanced file upload endpoint ready for future use" });
});

// ====== HEALTH CHECK ======
app.get("/", (req, res) => {
  res.json({ 
    status: "Ruth's AI Strategist Running!",
    features: ["Chat", "Memory", "Dynamic Personality", "Airtable Ready"]
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Ruth's AI Strategist running on ${PORT}`));
