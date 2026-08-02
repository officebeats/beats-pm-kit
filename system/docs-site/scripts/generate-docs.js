/**
 * Generate the public docs indexes from the canonical command registry and
 * active .agent skill tree.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const KIT_ROOT = path.resolve(__dirname, '..', '..', '..');
const DOCS_ROOT = path.resolve(__dirname, '..');
const REGISTRY_PATH = path.join(KIT_ROOT, '.agent', 'command-registry.json');
const CHECK_ONLY = process.argv.includes('--check');
const changedFiles = [];

function readRegistry() {
  const registry = JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf-8'));
  if (registry.schema_version !== 3) {
    throw new Error(`Unsupported command registry schema: ${registry.schema_version}`);
  }
  return registry;
}

function tableCell(value) {
  return String(value || '')
    .replace(/^['"]|['"]$/g, '')
    .replace(/\r?\n/g, ' ')
    .replace(/\|/g, '\\|')
    .trim();
}

function descriptionFromMarkdown(content) {
  const frontmatter = content.match(/^---\s*\r?\n([\s\S]*?)\r?\n---/);
  if (!frontmatter) return '';
  const lines = frontmatter[1].split(/\r?\n/);
  const index = lines.findIndex((line) => /^description:\s*/.test(line));
  if (index === -1) return '';
  const inline = lines[index].replace(/^description:\s*/, '').trim();
  if (inline && !['>', '>-', '|', '|-'].includes(inline)) return tableCell(inline);
  const continuation = [];
  for (const line of lines.slice(index + 1)) {
    if (!/^\s+/.test(line)) break;
    continuation.push(line.trim());
  }
  return tableCell(continuation.join(' '));
}

function replaceGeneratedBlock(file, marker, markdown) {
  const target = path.join(DOCS_ROOT, file);
  const content = fs.readFileSync(target, 'utf-8');
  const pattern = new RegExp(
    `<!-- GENERATED:${marker}:START -->[\\s\\S]*<!-- GENERATED:${marker}:END -->`,
  );
  if (!pattern.test(content)) throw new Error(`Missing ${marker} markers in ${file}`);
  writeGenerated(
    target,
    content.replace(
      pattern,
      `<!-- GENERATED:${marker}:START -->\n\n${markdown}\n<!-- GENERATED:${marker}:END -->`,
    ),
  );
}

function writeGenerated(target, content) {
  const current = fs.existsSync(target) ? fs.readFileSync(target, 'utf-8') : '';
  if (current === content) return;
  const relative = path.relative(KIT_ROOT, target).replace(/\\/g, '/');
  if (CHECK_ONLY) {
    changedFiles.push(relative);
    return;
  }
  fs.writeFileSync(target, content);
}

function generateSkillsIndex() {
  const skillsDir = path.join(KIT_ROOT, '.agent', 'skills');
  const skills = fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const skillFile = path.join(skillsDir, entry.name, 'SKILL.md');
      if (!fs.existsSync(skillFile)) return null;
      const content = fs.readFileSync(skillFile, 'utf-8');
      return { name: entry.name, description: descriptionFromMarkdown(content) };
    })
    .filter(Boolean)
    .sort((left, right) => left.name.localeCompare(right.name));

  const rows = skills.map(
    (skill) => `| \`${skill.name}\` | ${skill.description || 'Focused product-management capability.'} |`,
  );
  const table = ['| Skill | Description |', '|:---|:---|', ...rows].join('\n');
  replaceGeneratedBlock('skills/index.md', 'SKILLS', table);
  console.log(`Generated skills index: ${skills.length} skills`);
}

function workflowEntries(registry) {
  const entries = [];
  for (const [profile, commands] of Object.entries(registry.command_profiles)) {
    for (const name of commands) {
      const workflowFile = path.join(KIT_ROOT, '.agent', 'workflows', `${name}.md`);
      if (!fs.existsSync(workflowFile)) throw new Error(`Missing workflow for /${name}`);
      entries.push({
        name,
        profile: registry.execution_profiles[profile].title,
        description: descriptionFromMarkdown(fs.readFileSync(workflowFile, 'utf-8')),
      });
    }
  }
  return entries.sort((left, right) => left.name.localeCompare(right.name));
}

function generateWorkflowDocs(registry) {
  const workflows = workflowEntries(registry);
  const rows = workflows.map(
    (workflow) =>
      `| \`/${workflow.name}\` | ${workflow.profile} | ${workflow.description || 'Canonical kit workflow.'} |`,
  );
  const table = ['| Command | Profile | Purpose |', '|:---|:---|:---|', ...rows].join('\n');
  replaceGeneratedBlock('workflows/index.md', 'WORKFLOWS', table);

  const guide = [
    '# Commands Reference',
    '',
    'This command list is generated from `.agent/command-registry.json`, the routing source of truth.',
    '',
    table,
    '',
    'Natural-language requests remain supported. Use slash commands when deterministic routing is useful.',
    '',
  ].join('\n');
  writeGenerated(path.join(DOCS_ROOT, 'guide', 'commands.md'), guide);
  console.log(`Generated workflow docs: ${workflows.length} commands`);
}

console.log('Generating public documentation...');
const registry = readRegistry();
generateSkillsIndex();
generateWorkflowDocs(registry);
if (changedFiles.length) {
  console.error(`Generated documentation is stale: ${changedFiles.join(', ')}`);
  process.exitCode = 1;
} else if (CHECK_ONLY) {
  console.log('Generated documentation is current.');
}
console.log('Documentation generation complete.');
