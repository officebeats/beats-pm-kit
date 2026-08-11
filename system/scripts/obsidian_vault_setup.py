#!/usr/bin/env python3
"""Configure this Beats PM Kit checkout as a local Obsidian vault.

This script intentionally references the existing kit folder in place. It does
not mirror or copy files to another vault.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


SCRIPT_DIR = Path(__file__).resolve().parent
KIT_ROOT = SCRIPT_DIR.parent.parent

OBSIDIAN_DIRNAME = ".obsidian"
INDEX_RELATIVE_PATH = Path("6. Resources") / "obsidian" / "Obsidian Graph Index.md"

CORE_PLUGINS = {
    "file-explorer": True,
    "global-search": True,
    "switcher": True,
    "graph": True,
    "backlink": True,
    "canvas": True,
    "outgoing-link": True,
    "tag-pane": True,
    "properties": True,
    "page-preview": True,
    "daily-notes": True,
    "templates": True,
    "note-composer": True,
    "command-palette": True,
    "bookmarks": True,
    "outline": True,
    "file-recovery": True,
    "bases": True,
}

USER_IGNORE_FILTERS = [
    ".git/",
    ".beats/",
    ".agent/archive/",
    ".gemini/",
    ".claude/",
    ".codex/",
    ".kilocode/",
    ".context/",
    ".cline/",
    ".continue/",
    ".cursor/",
    ".trae/",
    ".windsurf/",
    ".zed/",
    ".github/",
    ".copilot/",
    ".kiro/",
    ".switchboard/",
    ".vscode/",
    ".mcp.json",
    "node_modules/",
    "__pycache__/",
    ".DS_Store",
    "system/tests/",
    "system/test_logs/",
    "system/debug_logs/",
    "system/reports/",
    "outputs/",
    "test_logs/",
    "artifacts/",
    "scratch/",
    "5. Trackers/MARKDOWN_LABELS.md",
    "Trackers/MARKDOWN_LABELS.md",
]

GRAPH_COLOR_GROUPS = [
    ("path:\"5. Trackers\"", 0xD64545),
    ("path:\"3. Meetings\"", 0x2D7DD2),
    ("path:\"4. People\"", 0x8E44AD),
    ("path:\"2. Products\"", 0x00A676),
    ("path:\"7. Partners\"", 0xF39C12),
    ("path:\"8. Clients\"", 0x16A085),
    ("path:\"6. SOPs\"", 0x6C7A89),
    ("path:\"6. Resources\"", 0x5D6DFF),
]

GRAPH_DEFAULTS = {
    "collapse-filter": True,
    "search": "",
    "showTags": True,
    "showAttachments": True,
    "hideUnresolved": False,
    "showOrphans": True,
    "collapse-color-groups": False,
    "collapse-display": True,
    "showArrow": True,
    "textFadeMultiplier": 0,
    "nodeSizeMultiplier": 1,
    "lineSizeMultiplier": 1,
    "collapse-forces": True,
    "centerStrength": 0.518713248970312,
    "repelStrength": 10,
    "linkStrength": 1,
    "linkDistance": 250,
    "scale": 1,
    "close": False,
}

DAILY_NOTES_DEFAULTS = {
    "format": "YYYY-MM-DD",
    "folder": "3. Meetings/daily-briefs",
    "template": "",
}

TEMPLATES_DEFAULTS = {
    "folder": ".agent/templates",
}


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return dict(default)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return dict(default)
    if not isinstance(data, dict):
        return dict(default)
    return data


def write_json(path: Path, data: dict, *, dry_run: bool) -> bool:
    rendered = json.dumps(data, indent=2, sort_keys=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == rendered:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return True


def merge_list(existing: list, additions: list) -> list:
    if not isinstance(existing, list):
        existing = []
    merged = list(existing)
    for item in additions:
        if item not in merged:
            merged.append(item)
    return merged


def graph_groups() -> list[dict]:
    return [{"query": query, "color": {"a": 1, "rgb": color}} for query, color in GRAPH_COLOR_GROUPS]


def merge_graph_groups(existing: list) -> list:
    if not isinstance(existing, list):
        existing = []
    merged = [item for item in existing if isinstance(item, dict)]
    existing_queries = {item.get("query") for item in merged}
    for item in graph_groups():
        if item["query"] not in existing_queries:
            merged.append(item)
    return merged


def index_content() -> str:
    return """# Obsidian Graph Index

> Local navigation index for the Beats PM Kit direct vault. Managed by `python3 system/scripts/obsidian_vault_setup.py --apply`.

## Core Hubs

- [[STATUS|Current Status]]
- [[SETTINGS|Settings]]
- [[5. Trackers/TASK_MASTER|Task Master]]
- [[5. Trackers/WEEKLY_PLAN|Weekly Plan]]
- [[5. Trackers/DECISION_LOG|Decision Log]]
- [[5. Trackers/STRATEGIC_INSIGHTS|Strategic Insights]]

## Human-readable Hubs

- [[5. Trackers/graph-hubs/Human-readable Hubs|Human-readable Hubs]]
- [[5. Trackers/graph-hubs/Workstream Hubs|Workstream Hubs]]
- [[5. Trackers/graph-hubs/Partner and the product Tasks|Partner and the product Tasks]]
- [[5. Trackers/graph-hubs/Meeting Evidence|Meeting Evidence]]

## Operating Areas

- [[1. Company|Company]]
- [[2. Products|Products]]
- [[3. Meetings|Meetings]]
- [[4. People|People]]
- [[5. Trackers|Trackers]]
- [[6. SOPs|SOPs]]
- [[6. Resources|Resources]]
- [[7. Partners|Partners]]
- [[8. Clients|Clients]]

## Tracker Hubs

- [[5. Trackers/tasks/_TEMPLATE|Task Template]]
- [[5. Trackers/projects/projects-master|Project Tracker]]
- [[5. Trackers/bugs/bugs-master|Bug Tracker]]
- [[5. Trackers/critical/boss-requests|Boss Requests]]

## Meeting And Evidence Lanes

- [[3. Meetings/transcripts|Transcripts]]
- [[3. Meetings/chat-transcripts|Chat Transcripts]]
- [[3. Meetings/reports|Reports]]
- [[3. Meetings/context-artifacts|Context Artifacts]]
- [[3. Meetings/quote-index|Quote Index]]

## Recommended Graph Filters

- Use `path:"5. Trackers"` for task state.
- Use `path:"4. People"` for stakeholder context.
- Use `path:"3. Meetings"` for meeting and evidence trails.
- Use `path:"7. Partners" OR path:"8. Clients"` for external relationship context.

"""


def write_text(path: Path, content: str, *, dry_run: bool) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def configure_vault(root: Path, *, dry_run: bool) -> list[str]:
    obsidian_dir = root / OBSIDIAN_DIRNAME
    changes: list[str] = []

    core_plugins_path = obsidian_dir / "core-plugins.json"
    core_plugins = read_json(core_plugins_path, {})
    core_plugins.update(CORE_PLUGINS)
    if write_json(core_plugins_path, core_plugins, dry_run=dry_run):
        changes.append(core_plugins_path.relative_to(root).as_posix())

    app_path = obsidian_dir / "app.json"
    app_config = read_json(app_path, {})
    app_config["alwaysUpdateLinks"] = True
    app_config["userIgnoreFilters"] = merge_list(app_config.get("userIgnoreFilters", []), USER_IGNORE_FILTERS)
    if write_json(app_path, app_config, dry_run=dry_run):
        changes.append(app_path.relative_to(root).as_posix())

    graph_path = obsidian_dir / "graph.json"
    graph_config = read_json(graph_path, GRAPH_DEFAULTS)
    for key, value in GRAPH_DEFAULTS.items():
        graph_config.setdefault(key, value)
    graph_config["showTags"] = True
    graph_config["showAttachments"] = True
    graph_config["showArrow"] = True
    graph_config["collapse-color-groups"] = False
    graph_config["colorGroups"] = merge_graph_groups(graph_config.get("colorGroups", []))
    if write_json(graph_path, graph_config, dry_run=dry_run):
        changes.append(graph_path.relative_to(root).as_posix())

    daily_notes_path = obsidian_dir / "daily-notes.json"
    daily_notes = read_json(daily_notes_path, DAILY_NOTES_DEFAULTS)
    for key, value in DAILY_NOTES_DEFAULTS.items():
        daily_notes.setdefault(key, value)
    if write_json(daily_notes_path, daily_notes, dry_run=dry_run):
        changes.append(daily_notes_path.relative_to(root).as_posix())

    templates_path = obsidian_dir / "templates.json"
    templates = read_json(templates_path, TEMPLATES_DEFAULTS)
    for key, value in TEMPLATES_DEFAULTS.items():
        templates.setdefault(key, value)
    if write_json(templates_path, templates, dry_run=dry_run):
        changes.append(templates_path.relative_to(root).as_posix())

    index_path = root / INDEX_RELATIVE_PATH
    if write_text(index_path, index_content(), dry_run=dry_run):
        changes.append(index_path.relative_to(root).as_posix())

    return changes


def open_index(root: Path) -> None:
    index_path = root / INDEX_RELATIVE_PATH
    uri = "obsidian://open?path=" + quote(str(index_path))
    subprocess.run(["open", uri], check=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure beats-pm-kit as a direct Obsidian vault.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    mode.add_argument("--apply", action="store_true", help="Write local Obsidian vault settings.")
    parser.add_argument("--open", action="store_true", help="Open the generated graph index in Obsidian after apply.")
    parser.add_argument("--root", type=Path, default=KIT_ROOT, help="Kit root. Defaults to this repository.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    dry_run = not args.apply

    if not root.exists():
        print(f"Kit root not found: {root}", file=sys.stderr)
        return 1

    changes = configure_vault(root, dry_run=dry_run)
    prefix = "DRY RUN: " if dry_run else ""
    if changes:
        print(f"{prefix}Obsidian direct-vault setup would update:" if dry_run else "Obsidian direct-vault setup updated:")
        for change in changes:
            print(f"- {change}")
    else:
        print(f"{prefix}Obsidian direct-vault setup is already current.")

    if args.open:
        if dry_run:
            print("Skipping --open during dry run.")
        else:
            open_index(root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
