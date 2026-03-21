import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseTaskMasterFile, writeTaskMasterFile } from './lib/taskmaster.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const BRAIN_ROOT = path.resolve(__dirname, '..', '..');
const TASK_FILE = path.join(BRAIN_ROOT, '5. Trackers', 'TASK_MASTER.md');

const app = express();
app.use(cors());
app.use(express.json());

// ── TaskMaster: uses shared lib (tested) ──────────────────────────
function parseTaskMaster() { return parseTaskMasterFile(TASK_FILE); }
function writeTaskMaster(active, archive, descriptions) { writeTaskMasterFile(TASK_FILE, active, archive, descriptions); }

// ── Generic Tracker Parser ────────────────────────────────────────

function parseChecklist(md) {
  const items = []; const lines = md.split(/\r?\n/); let section = '';
  for (const line of lines) {
    const sec = line.match(/^##\s+(.+)/); if (sec) { section = sec[1].trim(); continue; }
    const m = line.match(/^-\s+\[([ x\-\/])\]\s+(.+)/);
    if (m) {
      const ch = m[1]; const raw = m[2].trim();
      const pMatch = raw.match(/\[P(\d)\]/);
      const tags = (raw.match(/#(\w[\w-]*)/g) || []).map(t => t.slice(1));
      let status = 'open'; if (ch === 'x') status = 'done'; else if (ch === '-' || ch === '/') status = 'in-progress';
      items.push({ status, text: raw.replace(/\[P\d\]/g, '').replace(/#\w[\w-]*/g, '').trim(), priority: pMatch ? parseInt(pMatch[1]) : null, tags, section });
    }
  }
  return items;
}

function parseTable(md) {
  const lines = md.split(/\r?\n/).filter(l => l.trim().startsWith('|'));
  if (lines.length < 2) return [];
  const headers = lines[0].split('|').map(h => h.trim()).filter(Boolean);
  return lines.slice(1).filter(l => !l.match(/^\|\s*:?-/)).map(line => {
    const cells = line.split('|').map(c => c.trim()).filter(Boolean);
    const obj = {}; headers.forEach((h, i) => { obj[h] = cells[i] || ''; }); return obj;
  });
}

function readTracker(filename) {
  const fp = path.join(BRAIN_ROOT, '5. Trackers', filename);
  if (!fs.existsSync(fp)) return null;
  const content = fs.readFileSync(fp, 'utf-8');
  const hasTable = content.split(/\r?\n/).some(l => l.trim().startsWith('|'));
  return { name: filename.replace('.md', ''), items: hasTable ? parseTable(content) : parseChecklist(content), type: hasTable ? 'table' : 'checklist' };
}

// ── API: Tasks ────────────────────────────────────────────────────

app.get('/api/tasks', (req, res) => res.json(parseTaskMaster()));

app.patch('/api/tasks/:id/status', (req, res) => {
  const { status } = req.body;
  if (!status || typeof status !== 'string') return res.status(400).json({ error: 'Status required' });
  const data = parseTaskMaster();
  const task = data.active.find(t => t.id === req.params.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  task.status = status;
  writeTaskMaster(data.active, data.archive, data.descriptions);
  res.json({ ok: true, task });
});

app.patch('/api/tasks/:id', (req, res) => {
  const updates = req.body;
  const data = parseTaskMaster();
  const task = data.active.find(t => t.id === req.params.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  if (updates.task) task.task = updates.task;
  if (updates.priority) task.priority = updates.priority;
  if (updates.product) task.product = updates.product;
  if (updates.project) task.project = updates.project;
  if (updates.owner) task.owner = updates.owner;
  if (updates.due) task.due = updates.due;
  if (updates.tags) task.tags = updates.tags;
  if (updates.status) task.status = updates.status;
  if (typeof updates.description === 'string') data.descriptions[req.params.id] = updates.description;
  writeTaskMaster(data.active, data.archive, data.descriptions);
  res.json({ ok: true, task, description: data.descriptions[req.params.id] || '' });
});

app.post('/api/tasks/:id/archive', (req, res) => {
  const data = parseTaskMaster();
  const idx = data.active.findIndex(t => t.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Task not found' });
  const [task] = data.active.splice(idx, 1);
  task.status = 'Done';
  data.archive.push(task);
  writeTaskMaster(data.active, data.archive, data.descriptions);
  res.json({ ok: true });
});

app.post('/api/tasks/:id/unarchive', (req, res) => {
  const data = parseTaskMaster();
  const idx = data.archive.findIndex(t => t.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Task not found' });
  const [task] = data.archive.splice(idx, 1);
  task.status = 'Now';
  data.active.push(task);
  writeTaskMaster(data.active, data.archive, data.descriptions);
  res.json({ ok: true });
});

app.post('/api/tasks', (req, res) => {
  const { task, product, project, priority, owner, due, tags, description } = req.body;
  if (!task) return res.status(400).json({ error: 'Task text required' });
  const data = parseTaskMaster();
  const maxId = [...data.active, ...data.archive].map(t => parseInt((t.id || '').replace('T-', ''))).filter(n => !isNaN(n)).reduce((a, b) => Math.max(a, b), 0);
  const newTask = { id: `T-${String(maxId + 1).padStart(3, '0')}`, priority: priority || 'Normal', task, product: product || '', project: project || '', status: 'Now', owner: owner || '@me', due: due || '', tags: tags || [] };
  data.active.push(newTask);
  if (description) data.descriptions[newTask.id] = description;
  writeTaskMaster(data.active, data.archive, data.descriptions);
  res.json({ ok: true, task: newTask });
});

// ── API: Other Trackers ───────────────────────────────────────────

app.get('/api/trackers', (req, res) => {
  const files = ['BUG_TRACKER.md', 'BOSS_REQUESTS.md', 'PROJECT_TRACKER.md', 'ENG_TASKS.md', 'UX_TASKS.md', 'DECISION_LOG.md', 'DELEGATED_TASKS.md'];
  const trackers = {}; for (const f of files) { const t = readTracker(f); if (t) trackers[t.name] = t; }
  const vp = path.join(BRAIN_ROOT, 'VERSION');
  res.json({ trackers, version: fs.existsSync(vp) ? fs.readFileSync(vp, 'utf-8').trim() : '' });
});

app.get('/api/settings', (req, res) => {
  const fp = path.join(BRAIN_ROOT, 'SETTINGS.md');
  res.json({ content: fs.existsSync(fp) ? fs.readFileSync(fp, 'utf-8') : '' });
});

// ── API: Meeting Notes (recursive scan) ───────────────────────────

function scanMeetingsRecursive(dir, category) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    if (e.name.startsWith('.') || e.name === 'node_modules') continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      const subCat = e.name.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      results.push(...scanMeetingsRecursive(full, subCat));
    } else if (e.name.endsWith('.md')) {
      const content = fs.readFileSync(full, 'utf-8');
      const lines = content.split(/\r?\n/).filter(l => l.trim());
      const h1 = lines.find(l => l.match(/^#\s+/));
      const title = h1 ? h1.replace(/^#+\s*/, '').replace(/[\u{1F3AF}\u{1F4C5}\u{1F4DD}\u{26A1}\u{1F575}\u{1F3E2}\u{1F4C4}]/gu, '').trim() : e.name.replace('.md', '').replace(/_/g, ' ');
      const dateLine = lines.find(l => l.match(/\*\*Date\*\*/i));
      const dateMatch = dateLine ? dateLine.match(/(\d{4}-\d{2}-\d{2})/) : null;
      const fnDateMatch = e.name.match(/(\d{4}-\d{2}-\d{2})/);
      const date = dateMatch ? dateMatch[1] : fnDateMatch ? fnDateMatch[1] : null;
      const preview = lines.find(l => !l.startsWith('#') && !l.startsWith('**') && !l.startsWith('---') && !l.startsWith('>') && l.length > 10) || '';
      const stat = fs.statSync(full);
      const relPath = path.relative(path.join(BRAIN_ROOT, '3. Meetings'), full).replace(/\\/g, '/');
      results.push({
        title, date, category: category || 'General',
        preview: preview.slice(0, 150),
        path: '3. Meetings/' + relPath,
        filename: e.name,
        modified: stat.mtime.toISOString(),
        size: stat.size
      });
    }
  }
  return results;
}

app.get('/api/meetings', (req, res) => {
  const meetingsDir = path.join(BRAIN_ROOT, '3. Meetings');
  const notes = scanMeetingsRecursive(meetingsDir);
  notes.sort((a, b) => {
    if (a.date && b.date) return b.date.localeCompare(a.date);
    if (a.date) return -1;
    if (b.date) return 1;
    return new Date(b.modified) - new Date(a.modified);
  });
  const categories = [...new Set(notes.map(n => n.category))];
  res.json({ notes, categories, total: notes.length });
});

app.get('/api/files', (req, res) => {
  const dir = req.query.dir || '';
  const absPath = path.join(BRAIN_ROOT, dir);
  if (!fs.existsSync(absPath) || !fs.statSync(absPath).isDirectory()) return res.status(404).json({ error: 'Not found' });
  const entries = fs.readdirSync(absPath, { withFileTypes: true }).filter(e => !e.name.startsWith('.') && e.name !== 'node_modules')
    .map(e => ({ name: e.name, path: path.join(dir, e.name).replace(/\\/g, '/'), isDir: e.isDirectory() }));
  res.json({ path: dir, entries });
});

app.get('/api/file', (req, res) => {
  const fp = req.query.path || '';
  const abs = path.join(BRAIN_ROOT, fp);
  if (!fs.existsSync(abs) || fs.statSync(abs).isDirectory()) return res.status(404).json({ error: 'Not found' });
  res.json({ path: fp, content: fs.readFileSync(abs, 'utf-8') });
});

const PORT = 4401;
app.listen(PORT, () => console.log(`\n  🚀 BeatsPM Kit API → http://localhost:${PORT}\n  📁 Brain: ${BRAIN_ROOT}\n`));
