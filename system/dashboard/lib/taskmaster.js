// ── TaskMaster Parser/Writer — shared between server and tests ────
import fs from 'fs';

const LEGACY_DASHBOARD_HEADERS = ['id', 'priority', 'task', 'product', 'project', 'status', 'owner', 'due', 'tags'];
const CANONICAL_HEADERS = ['task', 'owner', 'due', 'status'];
const LEGACY_CANONICAL_HEADERS = ['id', 'task', 'owner', 'due', 'status'];

function normalizeHeaders(line = '') {
  return line
    .split('|')
    .slice(1, -1)
    .map(header => header.trim().toLowerCase());
}

function detectTaskMasterSchema(content) {
  const tableHeaderLine = (content || '').split(/\r?\n/).find(line => line.trim().startsWith('|'));
  if (!tableHeaderLine) return 'legacy-dashboard';

  const headers = normalizeHeaders(tableHeaderLine);
  if (headers.length === LEGACY_DASHBOARD_HEADERS.length && headers.every((header, index) => header === LEGACY_DASHBOARD_HEADERS[index])) {
    return 'legacy-dashboard';
  }
  if (
    (headers.length === CANONICAL_HEADERS.length && headers.every((header, index) => header === CANONICAL_HEADERS[index]))
    || (headers.length === LEGACY_CANONICAL_HEADERS.length && headers.every((header, index) => header === LEGACY_CANONICAL_HEADERS[index]))
  ) {
    return 'canonical';
  }
  return 'unknown';
}

export function canWriteTaskMaster(data) {
  return (data?.schema || 'legacy-dashboard') === 'legacy-dashboard';
}

export function parseTaskMaster(content) {
  if (!content) return { active: [], archive: [], descriptions: {}, schema: 'legacy-dashboard' };

  const schema = detectTaskMasterSchema(content);

  const descStart = content.indexOf('## Descriptions');
  const archiveStart = content.indexOf('## Archive');

  const activeSection = content.slice(0, descStart > -1 ? descStart : (archiveStart > -1 ? archiveStart : content.length));
  const descSection = descStart > -1 ? content.slice(descStart, archiveStart > -1 ? archiveStart : content.length) : '';
  const archiveSection = archiveStart > -1 ? content.slice(archiveStart) : '';

  const parseRows = (md) => {
    const lines = md.split(/\r?\n/).filter(l => l.trim().startsWith('|'));
    if (lines.length < 2) return [];
    const headers = lines[0].split('|').slice(1, -1).map(h => h.trim().toLowerCase());
    return lines.slice(1).filter(l => !l.match(/^\|\s*:?-/)).map(line => {
      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      const obj = {};
      headers.forEach((h, i) => { obj[h] = cells[i] || ''; });
      obj.tags = (obj.tags || '').split(',').map(t => t.trim()).filter(Boolean);
      obj.priority = (obj.priority || '').replace(/\*\*/g, '');
      obj.task = (obj.task || '').replace(/\*\*/g, '');
      const taskLink = obj.task.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (taskLink) {
        obj.task = taskLink[1];
        obj.id = obj.id || taskLink[2];
      }
      return obj;
    });
  };

  const descriptions = {};
  const descBlocks = descSection.split(/^### /m).slice(1);
  for (const block of descBlocks) {
    const lines = block.split(/\r?\n/);
    const id = lines[0].trim();
    const text = lines.slice(1).join('\n').trim();
    if (id) descriptions[id] = text;
  }

  return { active: parseRows(activeSection), archive: parseRows(archiveSection), descriptions, schema };
}

export function writeTaskMaster(active, archive, descriptions) {
  const header = `# Task Master (Active Ledger)

> Kanban columns: \`Now\` · \`Next\` · \`Later\` (+ custom columns)
> Mark tasks ✓ Done, then archive when ready.

| ID | Priority | Task | Product | Project | Status | Owner | Due | Tags |
| :- | :------- | :--- | :------ | :------ | :----- | :---- | :-- | :--- |
`;
  const activeRows = active.map(t =>
    `| ${t.id} | ${t.priority} | ${t.task} | ${t.product} | ${t.project} | ${t.status} | ${t.owner} | ${t.due} | ${t.tags.join(', ')} |`
  ).join('\n');

  let descBlock = '\n\n## Descriptions\n';
  for (const [id, text] of Object.entries(descriptions)) {
    if (text.trim()) descBlock += `\n### ${id}\n${text}\n`;
  }

  const archiveHeader = `\n## Archive

| ID | Priority | Task | Product | Project | Status | Owner | Due | Tags |
| :- | :------- | :--- | :------ | :------ | :----- | :---- | :-- | :--- |
`;
  const archiveRows = archive.map(t =>
    `| ${t.id} | ${t.priority} | ${t.task} | ${t.product} | ${t.project} | ${t.status} | ${t.owner} | ${t.due} | ${t.tags.join(', ')} |`
  ).join('\n');

  return header + activeRows + descBlock + archiveHeader + archiveRows + '\n';
}

export function parseTaskMasterFile(filepath) {
  if (!fs.existsSync(filepath)) return { active: [], archive: [], descriptions: {}, schema: 'legacy-dashboard' };
  return parseTaskMaster(fs.readFileSync(filepath, 'utf-8'));
}

export function writeTaskMasterFile(filepath, active, archive, descriptions) {
  fs.writeFileSync(filepath, writeTaskMaster(active, archive, descriptions));
}
