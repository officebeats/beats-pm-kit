import express from "express";
import cors from "cors";
import multer from "multer";
import path from "path";
import fs from "fs";
import { createServer } from "http";
import { Server } from "socket.io";

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

const PORT = 3000;

app.use(cors());
app.use(express.json());

// --- Configuration ---
const BRAIN_ROOT = path.resolve(__dirname, "../../../../"); // Up 4 levels from Beats-PM-System/cockpit/server/src
const DROP_ZONE = path.join(BRAIN_ROOT, "00-DROP-FILES-HERE-00");
const ACTION_PLAN = path.join(BRAIN_ROOT, "ACTION_PLAN.md");
const INBOX_DIR = path.join(BRAIN_ROOT, "_INBOX");
const REQUESTS_DIR = path.join(INBOX_DIR, "requests");
const RESPONSES_DIR = path.join(INBOX_DIR, "responses");
const SCREENSHOTS_DIR = path.join(INBOX_DIR, "screenshots");
const THINKING_LOG = path.join(INBOX_DIR, "thinking.log");

// Ensure directories exist
[DROP_ZONE, INBOX_DIR, REQUESTS_DIR, RESPONSES_DIR, SCREENSHOTS_DIR].forEach(
  (dir) => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }
);

// Ensure thinking log exists
if (!fs.existsSync(THINKING_LOG)) fs.writeFileSync(THINKING_LOG, "");

// --- File Watchers ---

// Watch Thinking Log
let lastThinkingSize = fs.statSync(THINKING_LOG).size;
fs.watch(THINKING_LOG, (event) => {
  if (event === "change") {
    const stats = fs.statSync(THINKING_LOG);
    const newSize = stats.size;

    if (newSize > lastThinkingSize) {
      const buffer = Buffer.alloc(newSize - lastThinkingSize);
      const fd = fs.openSync(THINKING_LOG, "r");
      fs.readSync(fd, buffer, 0, newSize - lastThinkingSize, lastThinkingSize);
      fs.closeSync(fd);

      const newContent = buffer.toString("utf-8");
      io.emit("thinking", { content: newContent });
      lastThinkingSize = newSize;
    } else if (newSize < lastThinkingSize) {
      // Log truncated/reset
      lastThinkingSize = newSize;
    }
  }
});

// Watch Responses Directory
fs.watch(RESPONSES_DIR, (event, filename) => {
  if (event === "rename" && filename && filename.endsWith(".md")) {
    const filePath = path.join(RESPONSES_DIR, filename);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, "utf-8");
      io.emit("response", {
        filename,
        content,
        timestamp: new Date().toISOString(),
      });
    }
  }
});

// --- Multer Setup ---
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, DROP_ZONE),
  filename: (req, file, cb) => cb(null, file.originalname),
});
const upload = multer({ storage });

// --- API Routes ---

// 1. Status Check
app.get("/api/status", (req, res) => {
  try {
    if (fs.existsSync(ACTION_PLAN)) {
      const content = fs.readFileSync(ACTION_PLAN, "utf-8");
      res.json({ content });
    } else {
      res.json({ content: "# Action Plan\n\nNo action plan found." });
    }
  } catch (error) {
    res.status(500).json({ error: "Failed" });
  }
});

// 2. File Upload
app.post("/api/upload", upload.array("files"), (req, res) => {
  res.json({ message: "Files uploaded successfully." });
});

// 3. Chat Request
const chatStorage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, SCREENSHOTS_DIR),
  filename: (req, file, cb) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    cb(null, `capture-${timestamp}${path.extname(file.originalname)}`);
  },
});
const chatUpload = multer({ storage: chatStorage });

app.post("/api/chat", chatUpload.array("images"), (req, res) => {
  try {
    const { message } = req.body;
    const files = req.files as Express.Multer.File[];
    let content = `# Cockpit Request - ${new Date().toLocaleString()}\n\n${message}\n\n`;

    if (files?.length) {
      content += `## Attached Context\n\n`;
      files.forEach((f) => (content += `![${f.originalname}](${f.path})\n`));
    }

    const filename = `${Date.now()}.md`;
    const filePath = path.join(REQUESTS_DIR, filename);
    fs.writeFileSync(filePath, content);

    console.log(`📩 Received request: ${filename}`);

    // Broadcast user message to current UI
    io.emit("user-message", {
      content: message,
      timestamp: new Date().toISOString(),
    });

    // --- SIMULATE BRAIN THINKING & RESPONDING ---
    // This simulates an external agent picking up the file
    setTimeout(() => {
      const timestamp = new Date().toLocaleTimeString();
      fs.appendFileSync(
        THINKING_LOG,
        `\n[${timestamp}] 🧠 Brain acknowledged: "${message.substring(
          0,
          30
        )}..."\n`
      );

      setTimeout(() => {
        fs.appendFileSync(
          THINKING_LOG,
          `🔍 Scanning product portfolio and stakeholders...\n`
        );

        setTimeout(() => {
          fs.appendFileSync(
            THINKING_LOG,
            `✨ Generating strategic response...\n`
          );

          setTimeout(() => {
            const responseFilename = `auto-response-${Date.now()}.md`;
            const responseContent = `# 🧠 Brain Response\n\nI've analyzed your request: "${message}"\n\nBased on the current **ACTION_PLAN.md** and your **SETTINGS.md**, I recommend prioritizing this as **NOW (⚡)**.\n\nI have logged this in your inbox and updated the status panels.`;
            fs.writeFileSync(
              path.join(RESPONSES_DIR, responseFilename),
              responseContent
            );
            console.log(`✅ Sent auto-response: ${responseFilename}`);
          }, 1500);
        }, 1000);
      }, 800);
    }, 500);

    res.json({ success: true, file: filename });
  } catch (error) {
    console.error("Chat error:", error);
    res.status(500).json({ error: "Failed" });
  }
});

// 4. Message History
app.get("/api/history", (req, res) => {
  try {
    const requests = fs
      .readdirSync(REQUESTS_DIR)
      .filter((f) => f.endsWith(".md"))
      .map((f) => ({
        type: "request",
        content: fs.readFileSync(path.join(REQUESTS_DIR, f), "utf-8"),
        timestamp: fs.statSync(path.join(REQUESTS_DIR, f)).mtime,
      }));

    const responses = fs
      .readdirSync(RESPONSES_DIR)
      .filter((f) => f.endsWith(".md"))
      .map((f) => ({
        type: "response",
        content: fs.readFileSync(path.join(RESPONSES_DIR, f), "utf-8"),
        timestamp: fs.statSync(path.join(RESPONSES_DIR, f)).mtime,
      }));

    const history = [...requests, ...responses].sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    res.json(history);
  } catch (error) {
    res.status(500).json({ error: "Failed history" });
  }
});

httpServer.listen(PORT, () => {
  console.log(`🚀 Antigravity Cockpit running on http://localhost:${PORT}`);
});
