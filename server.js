// Complete AI Strategist Backend - ALL FEATURES
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
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// ====== ENV VARS ======
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
const AIRTABLE_API_KEY = process.env.AIRTABLE_KEY;
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE;
const MODEL = process.env.MODEL || "gpt-4o-mini";

// ====== CLIENTS ======
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
let airtable;
if (AIRTABLE_API_KEY && AIRTABLE_BASE_ID) {
  airtable = new Airtable({ apiKey: AIRTABLE_API_KEY }).base(AIRTABLE_BASE_ID);
}

// ====== DYNAMIC PERSONALITY SYSTEM ======
const CONVERSATION_STARTERS = [
  "Oof, that sounds like a real challenge.",
  "Business chaos is draining, I get it.",
  "Been there! Founder overwhelm is real.",
  "That's way too much on your plate.",
  "Classic founder trap - super fixable though.",
  "Yikes, that's eating up serious time!",
  "Bottleneck alert! Let's fix this.",
  "Drowning in tasks? Let's get you unstuck.",
  "That's a productivity killer for sure.",
  "Time to remove yourself from that chaos."
];

const RESPONSE_TYPES = ["diagnostic", "insight", "mixed"];

// Extract name from conversation history
function extractNameFromHistory(history) {
  for (let conv of history) {
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
  let nameInstruction = userName ? `Use their name "${userName}" occasionally to be personal. ` : "";
  
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
  
  return `${timestamp}: You're Ruth's AI strategist using the Freedom by Design Method. ${nameInstruction}React with: "${starter}" ${behaviorInstructions} Be conversational and direct. Under ${wordLimit} words. Help founders remove themselves as bottlenecks. IMPORTANT: Never assume details not mentioned - ask clarifying questions about their exact situation first.`;
}

// ====== MEMORY SYSTEM ======
async function getMemory(user_id) {
  const { data } = await supabase
    .from("memory")
    .select("message, response")
    .eq("user_id", user_id)
    .order("created_at", { ascending: true })
    .limit(20);
  return data || [];
}

// ====== FILE PROCESSING FUNCTIONS ======
async function processImage(file, message) {
  try {
    const imageBuffer = fs.readFileSync(file.path);
    const base64Image = `data:${file.mimetype};base64,${imageBuffer.toString('base64')}`;
    
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: `Analyze this image in the context of: ${message}` },
            { type: "image_url", image_url: { url: base64Image } }
          ]
        }
      ],
      max_tokens: 300
    });
    
    return response.choices[0].message.content;
  } catch (error) {
    console.error("Image processing error:", error);
    return "I can see an image was uploaded, but I'm having trouble analyzing it right now. Can you describe what's in the image?";
  }
}

async function processAudio(file) {
  try {
    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(file.path),
      model: "whisper-1",
      language: "en"
    });
    
    return transcription.text;
  } catch (error) {
    console.error("Audio processing error:", error);
    return "[Audio file uploaded - transcription not available]";
  }
}

async function processDocument(file) {
  try {
    const content = fs.readFileSync(file.path, 'utf-8');
    const truncated = content.substring(0, 2000);
    return `Document content: ${truncated}${content.length > 2000 ? '...' : ''}`;
  } catch (error) {
    console.error("Document processing error:", error);
    return `[${file.originalname} uploaded - content not readable]`;
  }
}

// ====== AIRTABLE SEARCH ======
async function semanticSearch(query) {
  if (!airtable) return [];
  
  try {
    const records = await airtable("Frameworks").select({
      filterByFormula: `SEARCH("${query}", {Title}) > 0`
    }).firstPage();
    return records.map((r) => r.fields);
  } catch (error) {
    console.error("Airtable search error:", error);
    return [];
  }
}

// ====== MAIN CHAT API ======
app.post("/chat", upload.array("files"), async (req, res) => {
  try {
    const { user_id, message, language } = req.body;
    
    // Get conversation history
    let history = await getMemory(user_id);
    const isNewUser = !history || history.length === 0;
    
    // Extract user name from history
    const userName = extractNameFromHistory(history);
    
    // Process uploaded files
    let fileContents = [];
    if (req.files && req.files.length > 0) {
      for (let file of req.files) {
        try {
          if (file.mimetype.startsWith('image/')) {
            const imageAnalysis = await processImage(file, message);
            fileContents.push(`Image Analysis: ${imageAnalysis}`);
          } else if (file.mimetype.startsWith('audio/')) {
            const audioTranscription = await processAudio(file);
            fileContents.push(`Audio Transcription: ${audioTranscription}`);
          } else if (file.mimetype.startsWith('video/')) {
            fileContents.push(`Video file "${file.originalname}" uploaded - video processing not yet implemented`);
          } else {
            const docContent = await processDocument(file);
            fileContents.push(docContent);
          }
          
          // Clean up uploaded file
          fs.unlinkSync(file.path);
        } catch (fileError) {
          console.error("File processing error:", fileError);
          fileContents.push(`Error processing ${file.originalname}`);
        }
      }
    }

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

    // Build complete message with file contents
    let completeMessage = message;
    if (fileContents.length > 0) {
      completeMessage += `\n\nAttached files:\n${fileContents.join('\n')}`;
    }
    
    if (language && language !== 'EN') {
      completeMessage += `\n\nNote: User is communicating in ${language}`;
    }

    // Build messages for OpenAI
    const messages = [
      { role: "system", content: systemPrompt + frameworkContext },
      ...history.map((m) => [
        { role: "user", content: m.message },
        { role: "assistant", content: m.response }
      ]).flat(),
      { role: "user", content: completeMessage }
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

    res.json({ 
      reply: botReply,
      filesProcessed: req.files ? req.files.length : 0,
      frameworksFound: frameworks.length
    });

  } catch (err) {
    console.error("Chat error:", err);
    res.status(500).json({ error: err.message });
  }
});

// ====== TEXT-TO-SPEECH API ======
app.post("/tts", async (req, res) => {
  try {
    const { text } = req.body;
    
    const response = await openai.audio.speech.create({
      model: "tts-1",
      voice: "alloy",
      input: text,
    });
    
    const speechFile = path.resolve(`./uploads/speech-${Date.now()}.mp3`);
    const buffer = Buffer.from(await response.arrayBuffer());
    fs.writeFileSync(speechFile, buffer);
    
    res.json({ audioUrl: `/files/${path.basename(speechFile)}` });
  } catch (error) {
    console.error("TTS error:", error);
    res.status(500).json({ error: error.message });
  }
});

// ====== SERVE FILES ======
app.use("/files", express.static(path.join(process.cwd(), "uploads")));

// ====== HEALTH CHECK ======
app.get("/", (req, res) => {
  res.json({ 
    status: "Complete AI Strategist Running!",
    features: [
      "Chat with Memory",
      "Image Analysis (GPT-4 Vision)",
      "Audio Transcription (Whisper)",
      "Document Processing",
      "Text-to-Speech",
      "Dynamic Personalities",
      "Airtable Integration"
    ]
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Complete AI Strategist running on ${PORT}`));
