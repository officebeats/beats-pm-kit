"""Shared root, privacy, and local-runtime policy for Beats PM Kit."""

from __future__ import annotations

from pathlib import Path


PUBLIC_ROOT_FILES = {
    ".antigravityignore",
    ".cursorignore",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "ANTIGRAVITY.md",
    "CLAUDE.md",
    "CODEX_COMMANDS.md",
    "GEMINI.md",
    "OBSIDIAN.md",
    "README.md",
    "VERSION",
    "install.sh",
}

LOCAL_ONLY_ROOT_FILES = {
    ".cursorrules",
    ".cursorrules 2",
    ".initialized",
    ".mcp.json",
    "ACTION_PLAN.md",
    "BRAIN_DUMP.md",
    "CODEX_PROMPT.md",
    "CONVENTIONS.md",
    "DECISION_LOG.md",
    "SESSION_MEMORY.md",
    "SETTINGS.md",
    "STATUS.md",
    "requirements.txt",
    "task.md",
    "walkthrough.md",
    "implementation_plan.md",
}

DEPRECATED_ROOT_FILES = {
    ".gitkeep",
    "KERNEL.md",
    "debug_vacuum.py",
    "temp_copy.py",
}

PRIVATE_WORKSPACE_ROOTS = {
    "0. Incoming",
    "1. Company",
    "2. Products",
    "3. Meetings",
    "4. People",
    "5. Trackers",
    "6. SOPs",
    "7. Partners",
    "8. Clients",
}

OPTIONAL_WORKSPACE_ROOTS = {
    "6. Resources",
}

GENERATED_RUNTIME_DIRS = {
    ".beats",
    ".claude",
    ".cline",
    ".codex",
    ".context",
    ".continue",
    ".copilot",
    ".cursor",
    ".gemini",
    ".kilocode",
    ".kiro",
    ".obsidian",
    ".switchboard",
    ".trae",
    ".vscode",
    ".windsurf",
    ".zed",
}

LOCAL_RUNTIME_PREFIXES = {
    ".github/agents/",
    ".github/skills/",
    ".github/copilot-instructions.md",
    ".omx/",
    "_agent",
    "_agents",
    "cockpit/",
    "node_modules/",
}

LOCAL_RUNTIME_EXACT_PATHS = {
    ".mcp.json",
    ".cursorrules",
    ".cursorrules 2",
    "CODEX_PROMPT.md",
    "CONVENTIONS.md",
    "system/config.json",
}

ALLOWED_ROOT_DIRS = {
    ".agent",
    ".beats",
    ".git",
    ".github",
    ".githooks",
    "packs",
    "system",
    *PRIVATE_WORKSPACE_ROOTS,
    *OPTIONAL_WORKSPACE_ROOTS,
    *GENERATED_RUNTIME_DIRS,
}

LOCAL_CACHE_PATHS = {
    ".DS_Store",
    "system/content_index.json",
    "system/context_cache.json",
}

ROOT_CLEANUP_ARCHIVE = Path("0. Incoming") / "root-cleanup"


def normalize_path(path: str | Path) -> str:
    """Normalize a repo-relative path for policy checks."""
    return str(path).replace("\\", "/").lstrip("./")


def top_level(path: str | Path) -> str:
    """Return the first repo-relative path segment."""
    return normalize_path(path).split("/", 1)[0]


def generated_or_local_prefixes() -> tuple[str, ...]:
    """Return path prefixes that must never be tracked."""
    prefixes = {f"{name}/" for name in GENERATED_RUNTIME_DIRS}
    prefixes.update(LOCAL_RUNTIME_PREFIXES)
    return tuple(sorted(prefixes))


def is_private_workspace_content(path: str | Path) -> bool:
    """True when a path is private workspace content rather than skeleton."""
    normalized = normalize_path(path)
    root = top_level(normalized)
    if root not in PRIVATE_WORKSPACE_ROOTS:
        return False
    return not normalized.endswith("/.gitkeep")


def is_forbidden_tracked_path(path: str | Path) -> bool:
    """True when a path should not be part of the public repo."""
    normalized = normalize_path(path)
    if normalized in LOCAL_RUNTIME_EXACT_PATHS:
        return True
    if is_private_workspace_content(normalized):
        return True
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in generated_or_local_prefixes()
    )
