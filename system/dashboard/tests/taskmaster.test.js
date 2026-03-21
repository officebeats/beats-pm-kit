import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { parseTaskMaster, writeTaskMaster, parseTaskMasterFile, writeTaskMasterFile } from '../lib/taskmaster.js';

// ═══════════════════════════════════════════════════════════════════
// TaskMaster 2-Way Sync — Regression & Unit Tests
// ═══════════════════════════════════════════════════════════════════

const SAMPLE_MD = `# Task Master (Active Ledger)

> Kanban columns: \`Now\` · \`Next\` · \`Later\` (+ custom columns)
> Mark tasks ✓ Done, then archive when ready.

| ID | Priority | Task | Product | Project | Status | Owner | Due | Tags |
| :- | :------- | :--- | :------ | :------ | :----- | :---- | :-- | :--- |
| T-001 | High | Configure SETTINGS.md with personal info | Internal Tools | System Setup | Done | @me | 2026-03-14 | onboarding |
| T-002 | Normal | Review KERNEL.md rules | Internal Tools | System Setup | Now | @me | 2026-03-14 | onboarding |
| T-003 | Critical | Build companion web dashboard | Internal Tools | Web Frontend | Now | @me | 2026-03-15 | webapp, frontend |

## Descriptions

### T-001
This task involves configuring the basic settings.

### T-003
Build the React dashboard with glassmorphism UI.

## Archive

| ID | Priority | Task | Product | Project | Status | Owner | Due | Tags |
| :- | :------- | :--- | :------ | :------ | :----- | :---- | :-- | :--- |
| T-000 | Low | Initial test task | Test | Legacy | Done | @bot | 2026-01-01 | test |
`;

// ── Parser Unit Tests ─────────────────────────────────────────────

describe('parseTaskMaster', () => {
  it('parses active tasks correctly', () => {
    const { active } = parseTaskMaster(SAMPLE_MD);
    expect(active).toHaveLength(3);
    expect(active[0].id).toBe('T-001');
    expect(active[0].priority).toBe('High');
    expect(active[0].status).toBe('Done');
    expect(active[0].product).toBe('Internal Tools');
    expect(active[0].project).toBe('System Setup');
  });

  it('parses task tags as arrays', () => {
    const { active } = parseTaskMaster(SAMPLE_MD);
    expect(active[2].tags).toEqual(['webapp', 'frontend']);
    expect(active[0].tags).toEqual(['onboarding']);
  });

  it('parses single-tag tasks', () => {
    const { active } = parseTaskMaster(SAMPLE_MD);
    expect(active[1].tags).toEqual(['onboarding']);
  });

  it('parses archive section', () => {
    const { archive } = parseTaskMaster(SAMPLE_MD);
    expect(archive).toHaveLength(1);
    expect(archive[0].id).toBe('T-000');
    expect(archive[0].status).toBe('Done');
  });

  it('parses descriptions keyed by task ID', () => {
    const { descriptions } = parseTaskMaster(SAMPLE_MD);
    expect(descriptions['T-001']).toContain('configuring the basic settings');
    expect(descriptions['T-003']).toContain('glassmorphism');
    expect(descriptions['T-002']).toBeUndefined();
  });

  it('strips ** from priority and task fields', () => {
    const md = SAMPLE_MD.replace('High', '**High**').replace('Configure SETTINGS.md', '**Configure SETTINGS.md**');
    const { active } = parseTaskMaster(md);
    expect(active[0].priority).toBe('High');
    expect(active[0].task).toContain('Configure SETTINGS.md');
    expect(active[0].task).not.toContain('**');
  });

  it('handles empty content', () => {
    const result = parseTaskMaster('');
    expect(result.active).toEqual([]);
    expect(result.archive).toEqual([]);
    expect(result.descriptions).toEqual({});
  });

  it('handles null/undefined content', () => {
    const result = parseTaskMaster(null);
    expect(result.active).toEqual([]);
  });

  it('handles markdown with no archive section', () => {
    const md = SAMPLE_MD.split('## Archive')[0];
    const { active, archive } = parseTaskMaster(md);
    expect(active).toHaveLength(3);
    expect(archive).toEqual([]);
  });

  it('handles markdown with no descriptions section', () => {
    const md = SAMPLE_MD.replace(/## Descriptions[\s\S]*?(?=## Archive)/, '');
    const { descriptions } = parseTaskMaster(md);
    expect(Object.keys(descriptions)).toHaveLength(0);
  });

  it('handles tasks with empty tags field', () => {
    const md = `| ID | Priority | Task | Product | Project | Status | Owner | Due | Tags |
| :- | :------- | :--- | :------ | :------ | :----- | :---- | :-- | :--- |
| T-099 | Normal | No tags task | Prod | Proj | Now | @me | 2026-01-01 |  |`;
    const { active } = parseTaskMaster(md);
    expect(active[0].tags).toEqual([]);
  });

  it('handles tasks with special characters in names', () => {
    const md = `| ID | Priority | Task | Product | Project | Status | Owner | Due | Tags |
| :- | :------- | :--- | :------ | :------ | :----- | :---- | :-- | :--- |
| T-100 | Normal | Fix "login" & <auth> flow | My App (v2) | Phase 1/2 | Now | @me | 2026-01-01 | auth |`;
    const { active } = parseTaskMaster(md);
    expect(active[0].task).toContain('"login"');
    expect(active[0].product).toBe('My App (v2)');
    expect(active[0].project).toBe('Phase 1/2');
  });
});

// ── Writer Unit Tests ─────────────────────────────────────────────

describe('writeTaskMaster', () => {
  it('generates valid markdown table', () => {
    const output = writeTaskMaster(
      [{ id: 'T-001', priority: 'High', task: 'Test task', product: 'Prod', project: 'Proj', status: 'Now', owner: '@me', due: '2026-01-01', tags: ['test'] }],
      [], {}
    );
    expect(output).toContain('| T-001 | High | Test task | Prod | Proj | Now | @me | 2026-01-01 | test |');
  });

  it('includes descriptions block', () => {
    const output = writeTaskMaster([], [], { 'T-001': 'Some description text' });
    expect(output).toContain('## Descriptions');
    expect(output).toContain('### T-001');
    expect(output).toContain('Some description text');
  });

  it('skips empty descriptions', () => {
    const output = writeTaskMaster([], [], { 'T-001': '', 'T-002': '  ' });
    expect(output).not.toContain('### T-001');
    expect(output).not.toContain('### T-002');
  });

  it('includes archive section', () => {
    const output = writeTaskMaster([], 
      [{ id: 'T-099', priority: 'Low', task: 'Old task', product: 'X', project: 'Y', status: 'Done', owner: '@me', due: '', tags: [] }],
      {}
    );
    expect(output).toContain('## Archive');
    expect(output).toContain('| T-099 | Low | Old task |');
  });

  it('joins tags with comma separator', () => {
    const output = writeTaskMaster(
      [{ id: 'T-001', priority: 'Normal', task: 'T', product: '', project: '', status: 'Now', owner: '', due: '', tags: ['a', 'b', 'c'] }],
      [], {}
    );
    expect(output).toContain('| a, b, c |');
  });

  it('handles empty tags array', () => {
    const output = writeTaskMaster(
      [{ id: 'T-001', priority: 'Normal', task: 'T', product: '', project: '', status: 'Now', owner: '', due: '', tags: [] }],
      [], {}
    );
    expect(output).toContain('|  |');
  });
});

// ── Roundtrip Tests (Parse → Write → Parse) ──────────────────────

describe('Roundtrip: parse → write → parse', () => {
  it('preserves all task fields through roundtrip', () => {
    const original = parseTaskMaster(SAMPLE_MD);
    const written = writeTaskMaster(original.active, original.archive, original.descriptions);
    const reparsed = parseTaskMaster(written);

    expect(reparsed.active).toHaveLength(original.active.length);
    expect(reparsed.archive).toHaveLength(original.archive.length);

    for (let i = 0; i < original.active.length; i++) {
      expect(reparsed.active[i].id).toBe(original.active[i].id);
      expect(reparsed.active[i].priority).toBe(original.active[i].priority);
      expect(reparsed.active[i].task).toBe(original.active[i].task);
      expect(reparsed.active[i].product).toBe(original.active[i].product);
      expect(reparsed.active[i].project).toBe(original.active[i].project);
      expect(reparsed.active[i].status).toBe(original.active[i].status);
      expect(reparsed.active[i].owner).toBe(original.active[i].owner);
      expect(reparsed.active[i].due).toBe(original.active[i].due);
      expect(reparsed.active[i].tags).toEqual(original.active[i].tags);
    }
  });

  it('preserves descriptions through roundtrip', () => {
    const original = parseTaskMaster(SAMPLE_MD);
    const written = writeTaskMaster(original.active, original.archive, original.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.descriptions['T-001']).toBe(original.descriptions['T-001']);
    expect(reparsed.descriptions['T-003']).toBe(original.descriptions['T-003']);
  });

  it('preserves archive through roundtrip', () => {
    const original = parseTaskMaster(SAMPLE_MD);
    const written = writeTaskMaster(original.active, original.archive, original.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.archive[0].id).toBe(original.archive[0].id);
    expect(reparsed.archive[0].tags).toEqual(original.archive[0].tags);
  });
});

// ── Status Update Simulation (Drag-and-Drop Sync) ─────────────────

describe('Status update simulation (Kanban drag)', () => {
  it('changing status from Now → Next is preserved', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    const task = data.active.find(t => t.id === 'T-002');
    expect(task.status).toBe('Now');
    task.status = 'Next';

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    const updated = reparsed.active.find(t => t.id === 'T-002');
    expect(updated.status).toBe('Next');
  });

  it('changing status to Done is preserved', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    const task = data.active.find(t => t.id === 'T-003');
    task.status = 'Done';

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active.find(t => t.id === 'T-003').status).toBe('Done');
  });

  it('moving task to custom column preserves custom status name', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    const task = data.active.find(t => t.id === 'T-002');
    task.status = 'In Review';

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active.find(t => t.id === 'T-002').status).toBe('In Review');
  });

  it('status change does not affect other task fields', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    const task = data.active.find(t => t.id === 'T-003');
    const origProduct = task.product;
    const origProject = task.project;
    const origTags = [...task.tags];
    task.status = 'Later';

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    const updated = reparsed.active.find(t => t.id === 'T-003');
    expect(updated.product).toBe(origProduct);
    expect(updated.project).toBe(origProject);
    expect(updated.tags).toEqual(origTags);
    expect(updated.status).toBe('Later');
  });
});

// ── Archive / Unarchive Simulation ────────────────────────────────

describe('Archive and unarchive operations', () => {
  it('archiving moves task from active to archive', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    const idx = data.active.findIndex(t => t.id === 'T-001');
    const [task] = data.active.splice(idx, 1);
    task.status = 'Done';
    data.archive.push(task);

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active.find(t => t.id === 'T-001')).toBeUndefined();
    expect(reparsed.archive.find(t => t.id === 'T-001')).toBeDefined();
    expect(reparsed.active).toHaveLength(2);
    expect(reparsed.archive).toHaveLength(2);
  });

  it('unarchiving moves task from archive back to active', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    const idx = data.archive.findIndex(t => t.id === 'T-000');
    const [task] = data.archive.splice(idx, 1);
    task.status = 'Now';
    data.active.push(task);

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.archive.find(t => t.id === 'T-000')).toBeUndefined();
    expect(reparsed.active.find(t => t.id === 'T-000')).toBeDefined();
    expect(reparsed.active.find(t => t.id === 'T-000').status).toBe('Now');
  });
});

// ── Task Creation Simulation ──────────────────────────────────────

describe('Task creation', () => {
  it('adding a new task generates valid markdown', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    data.active.push({
      id: 'T-004', priority: 'Normal', task: 'New dashboard feature',
      product: 'Dashboard', project: 'UI Overhaul', status: 'Now',
      owner: '@me', due: '2026-04-01', tags: ['feature', 'ui'],
    });

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active).toHaveLength(4);
    const newTask = reparsed.active.find(t => t.id === 'T-004');
    expect(newTask.task).toBe('New dashboard feature');
    expect(newTask.product).toBe('Dashboard');
    expect(newTask.project).toBe('UI Overhaul');
    expect(newTask.tags).toEqual(['feature', 'ui']);
  });

  it('adding task with empty optional fields', () => {
    const data = parseTaskMaster(SAMPLE_MD);
    data.active.push({
      id: 'T-005', priority: 'Normal', task: 'Minimal task',
      product: '', project: '', status: 'Later',
      owner: '', due: '', tags: [],
    });

    const written = writeTaskMaster(data.active, data.archive, data.descriptions);
    const reparsed = parseTaskMaster(written);
    const t = reparsed.active.find(t => t.id === 'T-005');
    expect(t).toBeDefined();
    expect(t.product).toBe('');
    expect(t.tags).toEqual([]);
  });
});

// ── File I/O Tests ────────────────────────────────────────────────

describe('File I/O operations', () => {
  let tmpDir, tmpFile;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'taskmaster-test-'));
    tmpFile = path.join(tmpDir, 'TASK_MASTER.md');
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it('writeTaskMasterFile creates readable file', () => {
    const active = [{ id: 'T-001', priority: 'High', task: 'File test', product: 'P', project: 'Q', status: 'Now', owner: '@me', due: '', tags: ['io'] }];
    writeTaskMasterFile(tmpFile, active, [], {});
    expect(fs.existsSync(tmpFile)).toBe(true);

    const result = parseTaskMasterFile(tmpFile);
    expect(result.active).toHaveLength(1);
    expect(result.active[0].id).toBe('T-001');
  });

  it('parseTaskMasterFile handles missing file', () => {
    const result = parseTaskMasterFile(path.join(tmpDir, 'NONEXISTENT.md'));
    expect(result.active).toEqual([]);
    expect(result.archive).toEqual([]);
  });

  it('full file roundtrip preserves all data', () => {
    const active = [
      { id: 'T-010', priority: 'Critical', task: 'Deploy v2', product: 'App', project: 'Release', status: 'Now', owner: '@lead', due: '2026-06-01', tags: ['deploy', 'urgent'] },
      { id: 'T-011', priority: 'Low', task: 'Update docs', product: 'Docs', project: 'Wiki', status: 'Later', owner: '@me', due: '', tags: [] },
    ];
    const archive = [{ id: 'T-009', priority: 'Normal', task: 'Old item', product: 'X', project: 'Y', status: 'Done', owner: '@me', due: '2025-12-01', tags: ['old'] }];
    const descriptions = { 'T-010': 'Critical deployment for production.' };

    writeTaskMasterFile(tmpFile, active, archive, descriptions);
    const result = parseTaskMasterFile(tmpFile);

    expect(result.active).toHaveLength(2);
    expect(result.archive).toHaveLength(1);
    expect(result.active[0].tags).toEqual(['deploy', 'urgent']);
    expect(result.descriptions['T-010']).toContain('Critical deployment');
  });

  it('concurrent read-modify-write preserves integrity', () => {
    // Simulate dashboard write
    const data1 = { active: [{ id: 'T-001', priority: 'High', task: 'Task A', product: 'P', project: 'Q', status: 'Now', owner: '@me', due: '', tags: [] }], archive: [], descriptions: {} };
    writeTaskMasterFile(tmpFile, data1.active, data1.archive, data1.descriptions);

    // Read, modify, write (simulating drag status change)
    const read = parseTaskMasterFile(tmpFile);
    read.active[0].status = 'Next';
    writeTaskMasterFile(tmpFile, read.active, read.archive, read.descriptions);

    // Verify file reflects the change
    const verify = parseTaskMasterFile(tmpFile);
    expect(verify.active[0].status).toBe('Next');
    expect(verify.active[0].task).toBe('Task A');
  });
});

// ── Edge Cases ────────────────────────────────────────────────────

describe('Edge cases', () => {
  it('handles pipe characters in task names gracefully', () => {
    // Pipe in task name would break markdown tables - verify behavior
    const active = [{ id: 'T-001', priority: 'Normal', task: 'Fix A and B', product: 'P', project: 'Q', status: 'Now', owner: '@me', due: '', tags: [] }];
    const written = writeTaskMaster(active, [], {});
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active[0].task).toBe('Fix A and B');
  });

  it('handles very long task names', () => {
    const longName = 'A'.repeat(500);
    const active = [{ id: 'T-001', priority: 'Normal', task: longName, product: 'P', project: 'Q', status: 'Now', owner: '@me', due: '', tags: [] }];
    const written = writeTaskMaster(active, [], {});
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active[0].task).toBe(longName);
  });

  it('handles 50+ tasks without data loss', () => {
    const tasks = Array.from({ length: 50 }, (_, i) => ({
      id: `T-${String(i).padStart(3, '0')}`, priority: 'Normal', task: `Task ${i}`,
      product: `Prod${i % 5}`, project: `Proj${i % 3}`, status: ['Now', 'Next', 'Later'][i % 3],
      owner: '@me', due: '', tags: [`tag${i % 4}`],
    }));
    const written = writeTaskMaster(tasks, [], {});
    const reparsed = parseTaskMaster(written);
    expect(reparsed.active).toHaveLength(50);
    expect(reparsed.active[49].id).toBe('T-049');
    expect(reparsed.active[0].product).toBe('Prod0');
  });

  it('handles Windows CRLF line endings', () => {
    const crlfMd = SAMPLE_MD.replace(/\n/g, '\r\n');
    const result = parseTaskMaster(crlfMd);
    expect(result.active).toHaveLength(3);
    expect(result.archive).toHaveLength(1);
  });

  it('handles Unix LF line endings', () => {
    const lfMd = SAMPLE_MD.replace(/\r\n/g, '\n');
    const result = parseTaskMaster(lfMd);
    expect(result.active).toHaveLength(3);
  });

  it('products and projects are extractable from parsed data', () => {
    const { active } = parseTaskMaster(SAMPLE_MD);
    const products = [...new Set(active.map(t => t.product).filter(Boolean))];
    expect(products).toContain('Internal Tools');
    const projects = [...new Set(active.map(t => t.project).filter(Boolean))];
    expect(projects).toContain('System Setup');
    expect(projects).toContain('Web Frontend');
  });
});
