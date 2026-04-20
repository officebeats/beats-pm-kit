"""
Cross-CLI Adapter Sync Script
==============================
Ensures .agent/ is the single source of truth across all CLI tools.

Validates and repairs:
- Folder aliases: .agents, _agent, _agents -> .agent/
- CLI directories: .claude/, .kilocode/, .gemini/, .codex/ symlinks
- Config files: CLAUDE.md, AGENTS.md, and Codex rules generation

Usage:
    python system/scripts/sync_cli_adapters.py

Idempotent -- safe to run anytime. Intended for /regression and /vibe workflows.
"""

import os
import sys
import platform
import io
import re

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# --- Configuration ---

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CANONICAL = os.path.join(BASE_DIR, '.agent')
IS_WINDOWS = platform.system() == 'Windows'

# Folder aliases that should all point to .agent/
FOLDER_ALIASES = ['.agents', '_agent', '_agents']

# CLI directories that need internal symlinks to .agent/ subdirs
CLI_DIRS = {
    '.kilocode': ['agents', 'skills', 'templates', 'workflows', 'rules'],
    '.gemini':   ['agents', 'skills', 'templates', 'workflows'],
    '.codex':    ['agents', 'skills', 'templates', 'workflows'],
}

# Subdirectories to symlink inside CLI dirs (relative targets)
SUBDIR_TARGETS = {
    'agents':    os.path.join('..', '.agent', 'agents'),
    'skills':    os.path.join('..', '.agent', 'skills'),
    'templates': os.path.join('..', '.agent', 'templates'),
    'workflows': os.path.join('..', '.agent', 'workflows'),
    'rules':     os.path.join('..', '.agent', 'rules'),
}

results = []

# --- Helpers ---

def log_ok(msg):
    results.append(('[OK]', msg))
    print(f'  [OK] {msg}')

def log_fix(msg):
    results.append(('[FIX]', msg))
    print(f'  [FIX] {msg}')

def log_err(msg):
    results.append(('[ERR]', msg))
    print(f'  [ERR] {msg}')

def normalize_gemini_content(content):
    """Strip accidental generated headers before the real GEMINI heading."""
    marker = '# GEMINI.md'
    idx = content.find(marker)
    if idx > 0:
        return content[idx:]
    return content

def get_workflow_descriptions():
    """Return workflow names with a short description from frontmatter when available."""
    workflows_dir = os.path.join(CANONICAL, 'workflows')
    results = []
    if not os.path.isdir(workflows_dir):
        return results

    for filename in sorted(os.listdir(workflows_dir)):
        if not filename.endswith('.md'):
            continue
        name = filename[:-3]
        path = os.path.join(workflows_dir, filename)
        description = ''
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        match = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
        if match:
            description = match.group(1).strip().strip('"')
            if description in {'>-', '|', '|-', '>+', '|+'}:
                description = ''
        results.append((name, description))
    return results

def create_symlink(link_path, target, is_dir=True):
    """Create a symlink, handling Windows/Unix differences."""
    try:
        if os.path.islink(link_path) or os.path.exists(link_path):
            # Remove broken or existing link
            if os.path.islink(link_path):
                os.unlink(link_path)
            elif os.path.isfile(link_path):
                os.unlink(link_path)
        if IS_WINDOWS:
            os.symlink(target, link_path, target_is_directory=is_dir)
        else:
            os.symlink(target, link_path)
        return True
    except OSError as e:
        log_err(f'Failed to create symlink {link_path} -> {target}: {e}')
        return False

def is_valid_symlink(path, expected_target_name=None):
    """Check if a symlink exists and resolves to a real path."""
    if not os.path.islink(path):
        return False
    if not os.path.exists(path):
        return False  # Broken symlink
    return True

# ─── Phase 1: Folder Aliases ────────────────────────────────────────────────

def sync_folder_aliases():
    print('\nPhase 1: Folder Aliases (.agents, _agent, _agents -> .agent/)')
    for alias in FOLDER_ALIASES:
        link_path = os.path.join(BASE_DIR, alias)
        target = '.agent'

        if is_valid_symlink(link_path):
            log_ok(f'{alias} -> .agent/ (valid)')
        else:
            if create_symlink(link_path, target, is_dir=True):
                log_fix(f'{alias} -> .agent/ (repaired)')
            else:
                log_err(f'{alias} -> .agent/ (FAILED)')

# ─── Phase 2: CLI Directory Symlinks ────────────────────────────────────────

def sync_cli_directories():
    print('\nPhase 2: CLI Directory Symlinks')
    for cli_dir, subdirs in CLI_DIRS.items():
        cli_path = os.path.join(BASE_DIR, cli_dir)
        os.makedirs(cli_path, exist_ok=True)

        for subdir in subdirs:
            link_path = os.path.join(cli_path, subdir)
            target = SUBDIR_TARGETS[subdir]

            if is_valid_symlink(link_path):
                log_ok(f'{cli_dir}/{subdir} -> .agent/{subdir} (valid)')
            else:
                if create_symlink(link_path, target, is_dir=True):
                    log_fix(f'{cli_dir}/{subdir} -> .agent/{subdir} (repaired)')
                else:
                    log_err(f'{cli_dir}/{subdir} -> .agent/{subdir} (FAILED)')

# ─── Phase 3: CLAUDE.md Generation ──────────────────────────────────────────

def generate_claude_md():
    print('\nPhase 3: CLAUDE.md Generation')
    claude_dir = os.path.join(BASE_DIR, '.claude')
    os.makedirs(claude_dir, exist_ok=True)
    claude_md = os.path.join(claude_dir, 'CLAUDE.md')

    # Read the root GEMINI.md as the source
    gemini_path = os.path.join(CANONICAL, 'rules', 'GEMINI.md')
    if not os.path.exists(gemini_path):
        log_err('GEMINI.md not found at project root -- cannot generate CLAUDE.md')
        return

    with open(gemini_path, 'r', encoding='utf-8') as f:
        content = normalize_gemini_content(f.read())

    # Adapt for Claude Code: swap #hash triggers to /slash triggers
    content = content.replace('Instructional Memory for Gemini CLI', 'Instructional Memory for Claude Code')
    content = content.replace('Gemini CLI Agent Skills', 'Agent Skills')

    # Replace #command → /command in the command table
    import re
    content = re.sub(r'\| `#(\w+)`', r'| `/\1`', content)

    # Add Claude-specific header
    header = """# CLAUDE.md -- Auto-generated from GEMINI.md
# DO NOT EDIT THIS FILE DIRECTLY.
# Run: python system/scripts/sync_cli_adapters.py
# Source of truth: GEMINI.md + .agent/

"""
    final = header + content

    # Older repos may still have .claude/CLAUDE.md as a symlink to GEMINI.md.
    # Write via a temp file and atomically replace the destination so the symlink itself is replaced.
    if os.path.islink(claude_md):
        log_fix('.claude/CLAUDE.md symlink removed so a standalone adapter file can be generated')

    tmp_path = claude_md + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(final)
    os.replace(tmp_path, claude_md)
    log_ok(f'CLAUDE.md generated ({len(final)} bytes)')

# ─── Phase 4: AGENTS.md Generation (Codex) ──────────────────────────────────

def generate_agents_md():
    print('\nPhase 4: AGENTS.md Generation (Codex)')
    agents_md = os.path.join(BASE_DIR, 'AGENTS.md')

    # List current agents
    agents_dir = os.path.join(CANONICAL, 'agents')
    agents = []
    if os.path.isdir(agents_dir):
        agents = sorted([f.replace('.md', '') for f in os.listdir(agents_dir) if f.endswith('.md')])

    workflow_meta = get_workflow_descriptions()
    workflows = [name for name, _ in workflow_meta]

    # List current skills
    skills_dir = os.path.join(CANONICAL, 'skills')
    skill_count = 0
    if os.path.isdir(skills_dir):
        skill_count = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])

    content = f"""# AGENTS.md — Beats PM Antigravity Brain (Codex Adapter)

> **Auto-generated** by `sync_cli_adapters.py`. DO NOT EDIT DIRECTLY.
> Source of truth: `.agent/` directory.

## Architecture

This project uses a **Three-Tier Agent Architecture**:

1. **Identity Layer** (`.agent/agents/`) — Who does the work
2. **Orchestration Layer** (`.agent/workflows/`) — What sequence is triggered
3. **Capability Layer** (`.agent/skills/`) — How the work is done

## Codex Startup

On a new Codex session:

1. Read `SETTINGS.md` and `STATUS.md` first.
2. Treat `.agent/` as the source of truth.
3. When the user invokes `/command`, resolve it through `CODEX_COMMANDS.md`.
4. Load only the minimum `SKILL.md` files needed for the current task.
5. Translate Antigravity-only primitives into Codex equivalents instead of failing.
6. Write durable outputs back into the standard repo folders so runtime switching stays lossless.
7. For a manual re-bootstrap prompt, see `CODEX_PROMPT.md`.

## Slash Command Dispatch

If the user's message starts with `/command`:

1. Treat it as an explicit workflow invocation, not general conversation.
2. Resolve it using `CODEX_COMMANDS.md` or `.agent/workflows/<command>.md`.
3. Read that workflow before doing deeper work.
4. Use the rest of the user's message as workflow input.
5. Follow the workflow even if a natural-language interpretation also seems possible.
6. If the command does not exist, say it is unknown and point the user to `/help`.

## Available Agents ({len(agents)})

{chr(10).join(f'- `{a}`' for a in agents)}

## Available Workflows ({len(workflows)})

{chr(10).join(f'- `/{w}`' for w in workflows)}

## Skills: {skill_count} available

Skills are loaded on-demand from `.agent/skills/[skill-name]/SKILL.md`.

## Cross-CLI Aliases

All of these directories resolve to `.agent/`:
- `.agents/` · `_agent/` · `_agents/`
- `.claude/` · `.kilocode/` · `.gemini/` · `.codex/`

## Key Files

- `GEMINI.md` — Primary system config (Gemini CLI / Antigravity)
- `.claude/CLAUDE.md` — Claude Code adapter (auto-generated)
- `CODEX_COMMANDS.md` — Codex slash-command index (auto-generated)
- `.codex/rules.md` — Codex runtime notes (auto-generated)
- `AGENTS.md` — This file (Codex adapter)
- `SETTINGS.md` — User preferences
"""

    with open(agents_md, 'w', encoding='utf-8') as f:
        f.write(content)
    log_ok(f'AGENTS.md generated ({len(agents)} agents, {len(workflows)} workflows, {skill_count} skills)')

# ─── Phase 5: CODEX_COMMANDS.md Generation ──────────────────────────────────

def generate_codex_commands():
    print('\nPhase 5: CODEX_COMMANDS.md Generation')
    commands_md = os.path.join(BASE_DIR, 'CODEX_COMMANDS.md')
    workflow_meta = get_workflow_descriptions()

    content = """# Codex Command Index

This file makes slash-command routing explicit for Codex.

## Dispatch Rule

If the user's first non-whitespace token is `/command`:

1. Strip the leading `/`.
2. Look up the command in the table below.
3. Read the matching workflow file in `.agent/workflows/`.
4. Treat any remaining user text as workflow input.
5. If no match exists, report an unknown command and suggest `/help`.

## Commands

| Command | Workflow File | Purpose |
| :--- | :--- | :--- |
"""
    for name, description in workflow_meta:
        purpose = description or "See workflow file"
        content += f"| `/{name}` | `.agent/workflows/{name}.md` | {purpose} |\n"

    with open(commands_md, 'w', encoding='utf-8') as f:
        f.write(content)
    log_ok(f'CODEX_COMMANDS.md generated ({len(workflow_meta)} commands)')

# ─── Phase 6: .codex/rules.md Generation ────────────────────────────────────

def generate_codex_rules():
    print('\nPhase 6: .codex/rules.md Generation')
    codex_dir = os.path.join(BASE_DIR, '.codex')
    os.makedirs(codex_dir, exist_ok=True)
    codex_rules = os.path.join(codex_dir, 'rules.md')

    gemini_path = os.path.join(CANONICAL, 'rules', 'GEMINI.md')
    if not os.path.exists(gemini_path):
        log_err('GEMINI.md not found in .agent/rules -- cannot generate .codex/rules.md')
        return

    with open(gemini_path, 'r', encoding='utf-8') as f:
        content = normalize_gemini_content(f.read())

    header = """# rules.md -- Auto-generated from .agent/rules/GEMINI.md
# DO NOT EDIT THIS FILE DIRECTLY.
# Run: python system/scripts/sync_cli_adapters.py
# Primary Codex adapter: AGENTS.md

## Codex Runtime Notes

- Use `AGENTS.md` as the primary inventory of agents, workflows, and skills.
- On session start, read `SETTINGS.md` and `STATUS.md` before doing deeper work.
- When the user invokes `/command`, follow the explicit dispatch rule in `CODEX_COMMANDS.md`.
- Load only the `SKILL.md` files required for the current task.
- Translate Antigravity-only primitives into Codex equivalents instead of failing.
- Keep all durable output in the repo so Antigravity and Codex share the same state.
- For manual re-bootstrap, use `CODEX_PROMPT.md`.

## Slash Command Dispatch

If the user's first non-whitespace token is `/command`:

1. Treat it as a workflow invocation.
2. Resolve it through `CODEX_COMMANDS.md`.
3. Read the mapped `.agent/workflows/<command>.md` file before deeper work.
4. Use the remainder of the user's message as workflow input.
5. If no workflow exists, report an unknown command and suggest `/help`.

"""
    final = header + content

    with open(codex_rules, 'w', encoding='utf-8') as f:
        f.write(final)
    log_ok(f'.codex/rules.md generated ({len(final)} bytes)')

# ─── Phase 7: .claude/ Symlinks ─────────────────────────────────────────────

def sync_claude_dir():
    print('\nPhase 7: .claude/ Directory Sync')
    claude_dir = os.path.join(BASE_DIR, '.claude')
    os.makedirs(claude_dir, exist_ok=True)

    # Claude Code reads from .claude/commands/ for slash commands
    # We symlink it to workflows
    commands_link = os.path.join(claude_dir, 'commands')
    commands_target = os.path.join('..', '.agent', 'workflows')

    if is_valid_symlink(commands_link):
        log_ok('.claude/commands -> .agent/workflows (valid)')
    else:
        if create_symlink(commands_link, commands_target, is_dir=True):
            log_fix('.claude/commands -> .agent/workflows (repaired)')
        else:
            log_err('.claude/commands -> .agent/workflows (FAILED)')

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print('=' * 60)
    print('  Cross-CLI Adapter Sync')
    print(f'  Platform: {platform.system()} | Python: {sys.version.split()[0]}')
    print(f'  Base: {BASE_DIR}')
    print('=' * 60)

    if not os.path.isdir(CANONICAL):
        print(f'\n[FATAL] .agent/ directory not found at {CANONICAL}')
        sys.exit(1)

    sync_folder_aliases()
    sync_cli_directories()
    generate_claude_md()
    generate_agents_md()
    generate_codex_commands()
    generate_codex_rules()
    sync_claude_dir()

    # Summary
    ok_count = sum(1 for s, _ in results if s == '[OK]')
    fix_count = sum(1 for s, _ in results if s == '[FIX]')
    err_count = sum(1 for s, _ in results if s == '[ERR]')

    print('\n' + '=' * 60)
    print(f'  SUMMARY: {ok_count} OK · {fix_count} Repaired · {err_count} Failed')
    print('=' * 60)

    if err_count > 0:
        print('\n[WARN] Some operations failed. On Windows, symlink creation may require:')
        print('   - Run as Administrator, OR')
        print('   - Enable Developer Mode (Settings > For Developers > Developer Mode)')
        sys.exit(1)
    else:
        print('\n[OK] All CLI adapters are in sync.')

if __name__ == '__main__':
    main()
