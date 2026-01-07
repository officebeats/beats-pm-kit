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
// Improved logic to find the brain root (where KERNEL.md lives)
function findBrainRoot(startDir: string): string {
  let current = startDir;
  while (current !== path.parse(current).root) {
    if (fs.existsSync(path.join(current, "KERNEL.md"))) {
      return current;
    }
    current = path.dirname(current);
  }
  return startDir; // Fallback
}

const BRAIN_ROOT = findBrainRoot(process.cwd());
const STAGING_ROOT = path.join(BRAIN_ROOT, "0. Incoming", "staging");
const ACTION_PLAN = path.join(BRAIN_ROOT, "ACTION_PLAN.md");
const KERNEL_DOC = path.join(BRAIN_ROOT, "KERNEL.md");

console.log(`[Neural Link] Root: ${BRAIN_ROOT}`);
console.log(`[Neural Link] Staging: ${STAGING_ROOT}`);

const INBOX_DIR = path.join(STAGING_ROOT, "inbox");
const REQUESTS_DIR = path.join(INBOX_DIR, "requests");
const RESPONSES_DIR = path.join(INBOX_DIR, "responses");
const SCREENSHOTS_DIR = path.join(STAGING_ROOT, "screenshots");
const THINKING_LOG = path.join(STAGING_ROOT, "thinking.log");
const PRODUCTS_DIR = path.join(BRAIN_ROOT, "2. Products");
const PEOPLE_DIR = path.join(BRAIN_ROOT, "4. People");

// Ensure directories exist
[STAGING_ROOT, INBOX_DIR, REQUESTS_DIR, RESPONSES_DIR, SCREENSHOTS_DIR].forEach(
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

// Watch Action Plan
fs.watch(ACTION_PLAN, (event) => {
  if (event === "change") {
    try {
      const content = fs.readFileSync(ACTION_PLAN, "utf-8");
      io.emit("status-update", { content });
      console.log("⚡ Action Plan updated and broadcasted.");
    } catch (e) {
      console.error("Action Plan watch error", e);
    }
  }
});

// --- Multer Setup ---
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, STAGING_ROOT),
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

// 2. System Stats
app.get("/api/stats", (req, res) => {
  try {
    const peopleCount = fs.existsSync(PEOPLE_DIR)
      ? fs.readdirSync(PEOPLE_DIR).length
      : 0;
    const productsCount = fs.existsSync(PRODUCTS_DIR)
      ? fs.readdirSync(PRODUCTS_DIR).length
      : 0;

    // Simple mock for "Neural Storage" based on file count
    const totalFiles = peopleCount + productsCount || 1;
    const storagePercent = Math.min((totalFiles / 100) * 100, 100).toFixed(1);

    res.json({
      entities: peopleCount + productsCount,
      storagePercent: storagePercent,
      activeProjects: productsCount,
    });
  } catch (error) {
    res.status(500).json({ error: "Stats failed" });
  }
});

// 3. Kernel Documentation
app.get("/api/kernel", (req, res) => {
  try {
    if (fs.existsSync(KERNEL_DOC)) {
      const content = fs.readFileSync(KERNEL_DOC, "utf-8");
      res.json({ content });
    } else {
      res.json({ content: "# KERNEL.md not found." });
    }
  } catch (error) {
    res.status(500).json({ error: "Kernel failed" });
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

    console.log(`📩 Real Neural Intake: ${filename}`);

    // Broadcast user message to current UI
    io.emit("user-message", {
      content: message,
      timestamp: new Date().toISOString(),
    });

    // --- REAL INTEGRATION ---
    // The system now waits for an agent to process the file in 0. Incoming/staging/inbox/requests
    // No more simulation.

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
