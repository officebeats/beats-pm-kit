"""
Shared command registry helpers for cross-runtime workflow adapters.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_DIR = ROOT_DIR / ".agent"
REGISTRY_PATH = CANONICAL_DIR / "command-registry.json"
DESCRIPTION_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
MULTILINE_MARKERS = {"|-", "|", ">-", ">", "|+", ">+"}

DEFAULT_RUNTIME_PRIORITY = {
    "primary": "antigravity",
    "secondary": "codex",
    "compatibility": ["claude", "gemini", "kilocode", "other-clis"],
}


def get_root(root: Path | str | None = None) -> Path:
    """Return the repo root used for registry and workflow lookups."""
    return Path(root) if root is not None else ROOT_DIR


def get_registry_path(root: Path | str | None = None) -> Path:
    """Return the command registry path."""
    return get_root(root) / ".agent" / "command-registry.json"


def normalize_command_name(text: str) -> str:
    """Normalize a slash command or alias down to its first token."""
    stripped = text.strip()
    if not stripped:
        return ""
    token = stripped.split()[0]
    return token.lstrip("/").strip()


def get_workflow_descriptions(root: Path | str | None = None):
    """Return workflow names with descriptions parsed from frontmatter."""
    workflows_dir = get_root(root) / ".agent" / "workflows"
    workflow_meta = []

    if not workflows_dir.is_dir():
        return workflow_meta

    for path in sorted(workflows_dir.glob("*.md")):
        description = ""
        text = path.read_text(encoding="utf-8")
        match = DESCRIPTION_RE.search(text)
        if match:
            description = match.group(1).strip().strip('"')
            if description in MULTILINE_MARKERS:
                description = ""
        workflow_meta.append((path.stem, description))

    return workflow_meta


def load_command_registry(root: Path | str | None = None):
    """Load adapter metadata layered on top of workflow files."""
    path = get_registry_path(root)
    if not path.exists():
        return {"schema_version": 1, "runtime_priority": DEFAULT_RUNTIME_PRIORITY, "commands": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def get_runtime_priority(root: Path | str | None = None):
    """Return configured runtime priority, with safe defaults."""
    registry = load_command_registry(root)
    priority = dict(DEFAULT_RUNTIME_PRIORITY)
    priority.update(registry.get("runtime_priority", {}))
    return priority


def build_command_catalog(root: Path | str | None = None):
    """Merge workflow files with cross-runtime adapter metadata."""
    repo_root = get_root(root)
    workflow_meta = get_workflow_descriptions(repo_root)
    workflow_names = {name for name, _ in workflow_meta}
    registry = load_command_registry(repo_root)
    command_meta = registry.get("commands", {})

    unknown_commands = sorted(set(command_meta) - workflow_names)
    if unknown_commands:
        raise ValueError(
            "Command registry references workflows that do not exist: "
            + ", ".join(unknown_commands)
        )

    alias_owners = {}
    catalog = []

    for name, description in workflow_meta:
        override = command_meta.get(name, {})
        codex = override.get("codex", {})
        promotion = codex.get("promotion", "dispatch-only")
        if promotion not in {"dispatch-only", "skill"}:
            raise ValueError(f"Unsupported Codex promotion mode for /{name}: {promotion}")

        aliases = []
        for alias in override.get("aliases", []):
            normalized = normalize_command_name(alias)
            if not normalized or normalized == name or normalized in aliases:
                continue
            owner = alias_owners.get(normalized)
            if owner is not None and owner != name:
                raise ValueError(
                    f"Alias '/{normalized}' is assigned to both /{owner} and /{name}"
                )
            alias_owners[normalized] = name
            aliases.append(normalized)

        skill_name = codex.get("skill_name")
        if promotion == "skill" and not skill_name:
            raise ValueError(f"Promoted Codex command /{name} is missing skill_name")

        catalog.append(
            {
                "name": name,
                "workflow": f".agent/workflows/{name}.md",
                "description": description or "See workflow file",
                "aliases": aliases,
                "dangerous": bool(override.get("dangerous", False)),
                "note": override.get("note", ""),
                "codex_promotion": promotion,
                "codex_skill_name": skill_name,
                "codex_supporting_files": codex.get("supporting_files", []),
                "codex_optional_files": codex.get("optional_files", []),
            }
        )

    return catalog


def get_promoted_codex_commands(root: Path | str | None = None):
    """Return only commands promoted to Codex skill adapters."""
    return [entry for entry in build_command_catalog(root) if entry["codex_promotion"] == "skill"]


def resolve_command_name(command_text: str, root: Path | str | None = None):
    """Resolve a command or alias to its canonical workflow name."""
    normalized = normalize_command_name(command_text)
    if not normalized:
        return None

    alias_map = {}
    for entry in build_command_catalog(root):
        alias_map[entry["name"]] = entry["name"]
        for alias in entry["aliases"]:
            alias_map[alias] = entry["name"]

    return alias_map.get(normalized)
