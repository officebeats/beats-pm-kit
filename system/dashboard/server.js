import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const BRAIN_ROOT = path.resolve(__dirname, '..', '..');

const app = express();
app.use(cors());
app.use(express.json());

// ── Markdown Parsers ──────────────────────────────────────────────

function parseMarkdownTable(md) {
  const lines = md.split(/\r?\n/).filter(l => l.trim().startsWith('|'));
  if (lines.length < 2) return [];
  const headers = lines[0].split('|').map(h => h.trim()).filter(Boolean);
  const rows = lines.slice(2).map(line => {
    const cells = line.split('|').map(c => c.trim()).filter(Boolean);
    const obj = {};
    headers.forEach((h, i) => { obj[h] = cells[i] || ''; });
    return obj;
  });
  return rows;
}

function parseChecklistItems(md) {
  const items = [];
  const lines = md.split(/\r?\n/);
  let currentSection = '';
  for (const line of lines) {
    const sectionMatch = line.match(/^##\s+(.+)/);
    if (sectionMatch) {
      currentSection = sectionMatch[1].trim();
      continue;
    }
    const itemMatch = line.match(/^-\s+\[([ x\-\/])\]\s+(.+)/);
    if (itemMatch) {
      const statusChar = itemMatch[1];
      const text = itemMatch[2].trim();
      const priorityMatch = text.match(/\[P(\d)\]/);
      const tagsMatch = text.match(/#(\w[\w-]*)/g);
      let status = 'open';
      if (statusChar === 'x') status = 'done';
      else if (statusChar === '-' || statusChar === '/') status = 'in-progress';
      items.push({
        status,
        text: text.replace(/\[P\d\]/g, '').replace(/#\w[\w-]*/g, '').trim(),
        priority: priorityMatch ? parseInt(priorityMatch[1]) : null,
        tags: tagsMatch ? tagsMatch.map(t => t.slice(1)) : [],
        section: currentSection,
      });
    }
  }
  return items;
}

// ── API Routes ────────────────────────────────────────────────────

app.get('/api/status', (req, res) => {
  try {
    const trackersDir = path.join(BRAIN_ROOT, '5. Trackers');
    const trackerFiles = [
      'TASK_MASTER.md', 'BUG_TRACKER.md', 'BOSS_REQUESTS.md',
      'PROJECT_TRACKER.md', 'ENG_TASKS.md', 'UX_TASKS.md',
      'DECISION_LOG.md', 'DELEGATED_TASKS.md',
    ];

    const trackers = {};
    for (const file of trackerFiles) {
      const filePath = path.join(trackersDir, file);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf-8');
        const name = file.replace('.md', '');
        const hasTable = content.split(/\r?\n/).some(l => l.trim().startsWith('|'));
        trackers[name] = {
          name,
          file,
          items: hasTable ? parseMarkdownTable(content) : parseChecklistItems(content),
          type: hasTable ? 'table' : 'checklist',
          raw: content,
        };
      }
    }

    // Settings
    let settings = {};
    const settingsPath = path.join(BRAIN_ROOT, 'SETTINGS.md');
    if (fs.existsSync(settingsPath)) {
      settings.raw = fs.readFileSync(settingsPath, 'utf-8');
    }

    // Version
    let version = 'unknown';
    const versionPath = path.join(BRAIN_ROOT, 'VERSION');
    if (fs.existsSync(versionPath)) {
      version = fs.readFileSync(versionPath, 'utf-8').trim();
    }

    res.json({ trackers, settings, version, timestamp: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/tracker/:name', (req, res) => {
  try {
    const trackersDir = path.join(BRAIN_ROOT, '5. Trackers');
    const filePath = path.join(trackersDir, req.params.name + '.md');
    if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'Not found' });
    const content = fs.readFileSync(filePath, 'utf-8');
    const hasTable = content.split(/\r?\n/).some(l => l.trim().startsWith('|'));
    res.json({
      name: req.params.name,
      items: hasTable ? parseMarkdownTable(content) : parseChecklistItems(content),
      type: hasTable ? 'table' : 'checklist',
      raw: content,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = 4400;
app.listen(PORT, () => {
  console.log(`\n  🚀 Antigravity Dashboard API → http://localhost:${PORT}`);
  console.log(`  📁 Brain root: ${BRAIN_ROOT}\n`);
});
