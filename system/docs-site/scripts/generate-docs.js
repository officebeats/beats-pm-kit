/**
 * Auto-generates skill and workflow indexes for the docs site
 * by scanning .agent/skills/ and .agent/workflows/ directories.
 *
 * Usage: node scripts/generate-docs.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const BRAIN_ROOT = path.resolve(__dirname, '..', '..', '..');
const DOCS_ROOT = path.resolve(__dirname, '..');

// ── Generate Skills Index ─────────────────────────────────────────

function generateSkillsIndex() {
  const skillsDir = path.join(BRAIN_ROOT, '.agents', 'skills');
  if (!fs.existsSync(skillsDir)) {
    console.log('⚠ .agents/skills/ not found, skipping skills index');
    return;
  }

  const skills = [];
  const entries = fs.readdirSync(skillsDir, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const skillMd = path.join(skillsDir, entry.name, 'SKILL.md');
    if (!fs.existsSync(skillMd)) continue;

    const content = fs.readFileSync(skillMd, 'utf-8');
    // Extract description from frontmatter or first line
    const descMatch = content.match(/description:\s*(.+)/);
    const firstLine = content.split(/\r?\n/).find(l => l.trim() && !l.startsWith('---') && !l.startsWith('#'));
    const desc = descMatch ? descMatch[1].trim() : (firstLine || '').trim().slice(0, 120);

    skills.push({ name: entry.name, desc });
  }

  skills.sort((a, b) => a.name.localeCompare(b.name));

  let md = `| Skill | Description |\n|-------|-------------|\n`;
  for (const s of skills) {
    md += `| \`${s.name}\` | ${s.desc} |\n`;
  }

  const indexPath = path.join(DOCS_ROOT, 'skills', 'index.md');
  let indexContent = fs.readFileSync(indexPath, 'utf-8');
  indexContent = indexContent.replace(
    /<!-- GENERATED:SKILLS:START -->[\s\S]*<!-- GENERATED:SKILLS:END -->/,
    `<!-- GENERATED:SKILLS:START -->\n\n${md}\n<!-- GENERATED:SKILLS:END -->`
  );
  fs.writeFileSync(indexPath, indexContent);
  console.log(`✅ Generated skills index: ${skills.length} skills`);
}

// ── Generate Workflows Index ──────────────────────────────────────

function generateWorkflowsIndex() {
  const workflowsDir = path.join(BRAIN_ROOT, '.agents', 'workflows');
  if (!fs.existsSync(workflowsDir)) {
    console.log('⚠ .agents/workflows/ not found, skipping workflows index');
    return;
  }

  const workflows = [];
  const files = fs.readdirSync(workflowsDir).filter(f => f.endsWith('.md'));

  for (const file of files) {
    const content = fs.readFileSync(path.join(workflowsDir, file), 'utf-8');
    const descMatch = content.match(/description:\s*(.+)/);
    const name = file.replace('.md', '');
    const desc = descMatch ? descMatch[1].trim() : '';
    workflows.push({ name, desc });
  }

  workflows.sort((a, b) => a.name.localeCompare(b.name));

  let md = `| Command | Description |\n|---------|-------------|\n`;
  for (const w of workflows) {
    md += `| \`/${w.name}\` | ${w.desc} |\n`;
  }

  const indexPath = path.join(DOCS_ROOT, 'workflows', 'index.md');
  let indexContent = fs.readFileSync(indexPath, 'utf-8');
  indexContent = indexContent.replace(
    /<!-- GENERATED:WORKFLOWS:START -->[\s\S]*<!-- GENERATED:WORKFLOWS:END -->/,
    `<!-- GENERATED:WORKFLOWS:START -->\n\n${md}\n<!-- GENERATED:WORKFLOWS:END -->`
  );
  fs.writeFileSync(indexPath, indexContent);
  console.log(`✅ Generated workflows index: ${workflows.length} workflows`);
}

// ── Run ───────────────────────────────────────────────────────────

console.log('\n📚 Generating documentation...\n');
generateSkillsIndex();
generateWorkflowsIndex();
console.log('\n✨ Done!\n');
