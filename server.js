import express from "express";
import multer from "multer";
import fetch from "node-fetch";
import cors from "cors";
import { createClient } from "@supabase/supabase-js";
import { Configuration, OpenAIApi } from "openai";
import Airtable from "airtable";
import fs from "fs";
import path from "path";

const app = express();
const upload = multer({ dest: "uploads/" });
app.use(cors());
app.use(express.json());

// ====== ENV VARS ======
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID;
const MODEL = process.env.MODEL || "gpt-4o-mini"; // switchable to gpt-4.1

// ====== CLIENTS ======
const openai = new OpenAIApi(new Configuration({ apiKey: OPENAI_API_KEY }));
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
const airtable = new Airtable({ apiKey: AIRTABLE_API_KEY }).base(AIRTABLE_BASE_ID);

// ====== MEMORY (Supabase) ======
async function saveMessage(sessionId, role, content) {
  await supabase.from("memory").insert([{ session_id: sessionId, role, content }]);
}

async function getMemory(sessionId) {
  const { data } = await supabase
    .from("memory")
    .select("*")
    .eq("session_id", sessionId)
    .order("created_at", { ascending: true });
  return data || [];
}

// ====== SEMANTIC SEARCH (Airtable) ======
async function semanticSearch(query) {
  // Simple fetch — extend later with embeddings if needed
  const records = await airtable("frameworks").select().firstPage();
  return records.map((r) => r.fields);
}

// ====== API: Chat ======
app.post("/api/chat", upload.array("files"), async (req, res) => {
  try {
    const { message, sessionId, voiceReply } = req.body;
    let context = await getMemory(sessionId);

    // Save user message
    await saveMessage(sessionId, "user", message);

    // Build messages for OpenAI
    const messages = [
      { role: "system", content: "You are a warm, strategic AI assistant." },
      ...context.map((m) => ({ role: m.role, content: m.content })),
      { role: "user", content: message },
    ];

    // Attach files (if any)
    if (req.files.length > 0) {
      for (let file of req.files) {
        const fileContent = fs.readFileSync(file.path, "utf-8");
        messages.push({ role: "user", content: `File uploaded: ${file.originalname}\n${fileContent}` });
      }
    }

    // Query GPT
    const completion = await openai.createChatCompletion({
      model: MODEL,
      messages,
    });

    const reply = completion.data.choices[0].message.content;

    // Save assistant reply
    await saveMessage(sessionId, "assistant", reply);

    // Generate TTS if requested
    let audioUrl = null;
    if (voiceReply === "true") {
      const speechFile = path.resolve(`./speech-${Date.now()}.mp3`);
      const audioResp = await openai.createSpeech({
        model: "gpt-4o-mini-tts",
        voice: "alloy",
        input: reply,
      }, { responseType: "arraybuffer" });

      fs.writeFileSync(speechFile, Buffer.from(audioResp.data));
      audioUrl = `/files/${path.basename(speechFile)}`;
    }

    res.json({ reply, audioUrl });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

// ====== Serve generated files ======
app.use("/files", express.static(path.join(process.cwd(), "uploads")));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅ Server running on ${PORT}`));
