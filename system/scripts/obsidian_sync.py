#!/usr/bin/env python3
"""
obsidian_sync.py — Beats PM Kit → Obsidian Vault Sync

Copies content from the Kit's data folders (0-5) into the Obsidian vault
so Obsidian Sync can distribute to all devices. Adds YAML frontmatter
for Obsidian compatibility (tags, aliases, dates).

Usage:
    python3 obsidian_sync.py                # Full sync
    python3 obsidian_sync.py --dry-run      # Preview changes
    python3 obsidian_sync.py --folder 3     # Sync only Meetings
    python3 obsidian_sync.py --clean        # Remove stale files from vault
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
KIT_ROOT = SCRIPT_DIR.parent.parent  # beats-pm-kit/

# Default vault path — overridable via system/config.json
DEFAULT_VAULT = Path.home() / "Ernest0"
DEFAULT_TARGET_FOLDER = "Work"

# Folders to sync: kit_subfolder → obsidian_subfolder
SYNC_MAP = {
    "0. Incoming": "Incoming",
    "1. Company": "Company",
    "2. Products": "Products",
    "3. Meetings": "Meetings",
    "4. People": "People",
    "5. Trackers": "Trackers",
}

# Files/patterns to skip during sync
SKIP_PATTERNS = [
    ".gitkeep",
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    "*.bak",
    ".git",
]

# Tag inference from folder
FOLDER_TAGS = {
    "Incoming": ["inbox"],
    "Company": ["company", "strategy"],
    "Products": ["product", "prd"],
    "Meetings": ["meeting", "notes"],
    "People": ["people", "stakeholder"],
    "Trackers": ["tracker", "task"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config():
    """Load vault path from system/config.json if available."""
    config_path = KIT_ROOT / "system" / "config.json"
    vault_path = DEFAULT_VAULT
    target_folder = DEFAULT_TARGET_FOLDER

    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg = json.load(f)
            obs = cfg.get("obsidian", {})
            if obs.get("vault_path"):
                vault_path = Path(obs["vault_path"]).expanduser()
            if obs.get("target_folder"):
                target_folder = obs["target_folder"]
        except (json.JSONDecodeError, KeyError):
            pass

    return vault_path, target_folder


def should_skip(path: Path) -> bool:
    """Check if a file/dir should be skipped."""
    name = path.name
    for pattern in SKIP_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def file_hash(path: Path) -> str:
    """Quick hash to detect changes."""
    h = hashlib.md5()
    try:
        h.update(path.read_bytes())
    except OSError:
        return ""
    return h.hexdigest()


def has_frontmatter(content: str) -> bool:
    """Check if markdown already has YAML frontmatter."""
    return content.startswith("---\n")


def build_frontmatter(file_path: Path, folder_tag: str) -> str:
    """Generate YAML frontmatter for Obsidian."""
    stat = file_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
    title = file_path.stem.replace("-", " ").replace("_", " ")

    tags = FOLDER_TAGS.get(folder_tag, [])
    tags_str = "\n".join(f"  - {t}" for t in tags)

    frontmatter = f"""---
title: "{title}"
source: beats-pm-kit
synced: {datetime.now().strftime("%Y-%m-%d %H:%M")}
modified: {modified}
tags:
{tags_str}
---

"""
    return frontmatter


def sync_file(src: Path, dst: Path, folder_tag: str, dry_run: bool = False) -> str:
    """Sync a single file. Returns status: 'new', 'updated', 'skipped'."""

    # Only process markdown files — copy others directly
    is_markdown = src.suffix.lower() in (".md", ".markdown")

    if dst.exists():
        if file_hash(src) == file_hash(dst):
            return "skipped"
        status = "updated"
    else:
        status = "new"

    if dry_run:
        return status

    dst.parent.mkdir(parents=True, exist_ok=True)

    if is_markdown:
        content = src.read_text(encoding="utf-8", errors="replace")

        # Strip existing sync frontmatter if re-syncing
        if has_frontmatter(content):
            # Check if it's our frontmatter (has 'source: beats-pm-kit')
            end = content.find("---\n", 4)
            if end != -1:
                fm_block = content[4:end]
                if "source: beats-pm-kit" in fm_block:
                    content = content[end + 4:].lstrip("\n")

        # Only add frontmatter if the file doesn't already have non-kit frontmatter
        if not has_frontmatter(content):
            frontmatter = build_frontmatter(src, folder_tag)
            content = frontmatter + content

        dst.write_text(content, encoding="utf-8")
    else:
        shutil.copy2(src, dst)

    return status


def clean_stale(vault_target: Path, kit_sources: dict, dry_run: bool = False) -> list:
    """Remove files from vault that no longer exist in the Kit."""
    removed = []
    for obs_folder, kit_folder in kit_sources.items():
        obs_path = vault_target / obs_folder
        if not obs_path.exists():
            continue
        for f in obs_path.rglob("*"):
            if f.is_dir() or should_skip(f):
                continue
            rel = f.relative_to(obs_path)
            src = kit_folder / rel
            if not src.exists():
                removed.append(str(f))
                if not dry_run:
                    f.unlink()
    return removed


# ---------------------------------------------------------------------------
# Main Sync
# ---------------------------------------------------------------------------

def run_sync(args):
    vault_path, target_folder = load_config()
    vault_target = vault_path / target_folder

    if not vault_path.exists():
        print(f"❌ Obsidian vault not found at: {vault_path}")
        sys.exit(1)

    # Filter to specific folder if requested
    sync_folders = SYNC_MAP
    if args.folder:
        key = None
        for k, v in SYNC_MAP.items():
            if args.folder in k or args.folder == v:
                key = k
                break
        if not key:
            print(f"❌ Unknown folder: {args.folder}")
            print(f"   Available: {', '.join(SYNC_MAP.keys())}")
            sys.exit(1)
        sync_folders = {key: SYNC_MAP[key]}

    print(f"{'🔍 DRY RUN — ' if args.dry_run else ''}Syncing Kit → Obsidian")
    print(f"   Kit:    {KIT_ROOT}")
    print(f"   Vault:  {vault_target}")
    print()

    stats = {"new": 0, "updated": 0, "skipped": 0}
    kit_sources = {}  # for clean

    for kit_folder_name, obs_folder_name in sync_folders.items():
        kit_folder = KIT_ROOT / kit_folder_name
        obs_folder = vault_target / obs_folder_name
        kit_sources[obs_folder_name] = kit_folder

        if not kit_folder.exists():
            continue

        for src in kit_folder.rglob("*"):
            if src.is_dir() or should_skip(src):
                continue

            rel = src.relative_to(kit_folder)
            dst = obs_folder / rel

            status = sync_file(src, dst, obs_folder_name, dry_run=args.dry_run)
            stats[status] += 1

            if status != "skipped":
                icon = "✨" if status == "new" else "🔄"
                print(f"   {icon} [{status.upper()}] {obs_folder_name}/{rel}")

    # Clean stale files
    if args.clean and not args.dry_run:
        removed = clean_stale(vault_target, kit_sources)
        for r in removed:
            print(f"   🗑  [REMOVED] {r}")
        stats["removed"] = len(removed)

    print()
    print(f"✅ Done — {stats['new']} new, {stats['updated']} updated, {stats['skipped']} unchanged")

    # Write sync metadata
    if not args.dry_run:
        meta_file = vault_target / ".sync_meta.json"
        meta = {
            "last_sync": datetime.now().isoformat(),
            "source": str(KIT_ROOT),
            "stats": stats,
        }
        meta_file.write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Beats PM Kit → Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Preview without copying")
    parser.add_argument("--folder", type=str, help="Sync only this folder (e.g., '3' or 'Meetings')")
    parser.add_argument("--clean", action="store_true", help="Remove stale files from vault")
    args = parser.parse_args()
    run_sync(args)
