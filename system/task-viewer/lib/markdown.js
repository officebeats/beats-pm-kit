import fs from 'fs';
import path from 'path';

const BRAIN_ROOT = path.resolve(process.cwd(), '../..');

/**
 * Parse a markdown table into an array of objects.
 */
export function parseTable(md) {
  const lines = md.split(/\r?\n/).filter(l => l.trim().startsWith('|'));
  if (lines.length < 2) return [];
  const headers = lines[0].split('|').map(h => h.trim()).filter(Boolean);
  return lines.slice(2).map(line => {
    const cells = line.split('|').map(c => c.trim()).filter(Boolean);
    const obj = {};
    headers.forEach((h, i) => { obj[h] = cells[i] || ''; });
    return obj;
  });
}

/**
 * Parse markdown checklist items (- [ ] / - [x] / - [-]) with priority, tags, sections.
 */
export function parseChecklist(md) {
  const items = [];
  const lines = md.split(/\r?\n/);
  let section = '';
  for (const line of lines) {
    const secMatch = line.match(/^##\s+(.+)/);
    if (secMatch) { section = secMatch[1].trim(); continue; }
    const m = line.match(/^-\s+\[([ x\-\/])\]\s+(.+)/);
    if (m) {
      const statusChar = m[1];
      const raw = m[2].trim();
      const pMatch = raw.match(/\[P(\d)\]/);
      const tags = (raw.match(/#(\w[\w-]*)/g) || []).map(t => t.slice(1));
      let status = 'open';
      if (statusChar === 'x') status = 'done';
      else if (statusChar === '-' || statusChar === '/') status = 'in-progress';
      items.push({
        status,
        text: raw.replace(/\[P\d\]/g, '').replace(/#\w[\w-]*/g, '').trim(),
        priority: pMatch ? parseInt(pMatch[1]) : null,
        tags,
        section,
      });
    }
  }
  return items;
}

/**
 * Read a single tracker file and return parsed data.
 */
export function readTracker(filename) {
  const fp = path.join(BRAIN_ROOT, '5. Trackers', filename);
  if (!fs.existsSync(fp)) return null;
  const content = fs.readFileSync(fp, 'utf-8');
  const hasTable = content.split(/\r?\n/).some(l => l.trim().startsWith('|'));
  return {
    name: filename.replace('.md', ''),
    file: filename,
    items: hasTable ? parseTable(content) : parseChecklist(content),
    type: hasTable ? 'table' : 'checklist',
    raw: content,
  };
}

/**
 * Read all tracker files.
 */
export function readAllTrackers() {
  const files = [
    'TASK_MASTER.md', 'BUG_TRACKER.md', 'BOSS_REQUESTS.md',
    'PROJECT_TRACKER.md', 'ENG_TASKS.md', 'UX_TASKS.md',
    'DECISION_LOG.md', 'DELEGATED_TASKS.md',
  ];
  const trackers = {};
  for (const f of files) {
    const t = readTracker(f);
    if (t) trackers[t.name] = t;
  }
  return trackers;
}

/**
 * Read VERSION file.
 */
export function readVersion() {
  const fp = path.join(BRAIN_ROOT, 'VERSION');
  return fs.existsSync(fp) ? fs.readFileSync(fp, 'utf-8').trim() : 'unknown';
}

/**
 * Read SETTINGS.md.
 */
export function readSettings() {
  const fp = path.join(BRAIN_ROOT, 'SETTINGS.md');
  return fs.existsSync(fp) ? fs.readFileSync(fp, 'utf-8') : '';
}

/**
 * List files in a directory (for file browser).
 */
export function listDirectory(relPath) {
  const absPath = path.join(BRAIN_ROOT, relPath);
  if (!fs.existsSync(absPath)) return [];
  const entries = fs.readdirSync(absPath, { withFileTypes: true });
  return entries
    .filter(e => !e.name.startsWith('.') && e.name !== 'node_modules')
    .map(e => ({
      name: e.name,
      path: path.join(relPath, e.name).replace(/\\/g, '/'),
      isDir: e.isDirectory(),
    }));
}

/**
 * Read a file's contents (for markdown preview).
 */
export function readFile(relPath) {
  const absPath = path.join(BRAIN_ROOT, relPath);
  if (!fs.existsSync(absPath)) return null;
  if (fs.statSync(absPath).isDirectory()) return null;
  return fs.readFileSync(absPath, 'utf-8');
}
