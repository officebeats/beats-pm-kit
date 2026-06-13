#!/usr/bin/env python3
"""Keep the Beats PM Kit root clean without deleting user work."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.root_policy import (
    ALLOWED_ROOT_DIRS,
    DEPRECATED_ROOT_FILES,
    LOCAL_CACHE_PATHS,
    LOCAL_ONLY_ROOT_FILES,
    PUBLIC_ROOT_FILES,
    ROOT_CLEANUP_ARCHIVE,
)


GENERATED_DUPLICATE_DIRS = (
    Path(".kilocode") / "agents 2",
    Path(".kilocode") / "rules 2",
    Path(".kilocode") / "skills 2",
    Path(".kilocode") / "templates 2",
    Path(".kilocode") / "templates 3",
    Path(".kilocode") / "workflows 2",
    Path(".kilocode") / "workflows 3",
)

LOG_DIRS_TO_ARCHIVE = (
    Path("test_logs"),
    Path("system") / "test_logs",
)


@dataclass(frozen=True)
class CleanAction:
    action: str
    path: str
    destination: str = ""
    reason: str = ""


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def timestamp_value(value: str | None = None) -> str:
    if value:
        return value
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def archive_destination(root: Path, path: Path, stamp: str) -> Path:
    return root / ROOT_CLEANUP_ARCHIVE / stamp / relpath(path, root)


def move_path(source: Path, destination: Path, *, apply: bool) -> None:
    if not apply:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        suffix = 1
        candidate = destination
        while candidate.exists():
            candidate = destination.with_name(f"{destination.name}.{suffix}")
            suffix += 1
        destination = candidate
    shutil.move(str(source), str(destination))


def remove_path(path: Path, *, apply: bool) -> None:
    if not apply:
        return
    if path.is_dir():
        path.rmdir()
    else:
        path.unlink()


def is_empty_dir(path: Path) -> bool:
    try:
        return path.is_dir() and not any(path.iterdir())
    except OSError:
        return False


def root_actions(root: Path, *, stamp: str) -> list[CleanAction]:
    actions: list[CleanAction] = []
    archive_root = root / ROOT_CLEANUP_ARCHIVE

    for rel in sorted(LOCAL_CACHE_PATHS):
        path = root / rel
        if path.exists() and path.is_file():
            actions.append(CleanAction("remove_file", rel, reason="local-cache"))

    for rel in GENERATED_DUPLICATE_DIRS:
        path = root / rel
        if path.exists() and is_empty_dir(path):
            actions.append(CleanAction("remove_empty_dir", rel.as_posix(), reason="empty-generated-duplicate"))

    for rel in LOG_DIRS_TO_ARCHIVE:
        path = root / rel
        if path.exists():
            destination = archive_destination(root, path, stamp)
            actions.append(
                CleanAction(
                    "move",
                    rel.as_posix(),
                    relpath(destination, root),
                    "legacy-log-dir",
                )
            )

    if not root.exists():
        return actions

    handled_root_names = {rel.parts[0] for rel in LOG_DIRS_TO_ARCHIVE if len(rel.parts) == 1}
    for item in sorted(root.iterdir(), key=lambda value: value.name.lower()):
        name = item.name
        if name in {".", ".."}:
            continue
        if name in handled_root_names:
            continue
        if item == archive_root or archive_root in item.parents:
            continue
        if item.is_file():
            if name in PUBLIC_ROOT_FILES or name in LOCAL_ONLY_ROOT_FILES:
                continue
            if name in DEPRECATED_ROOT_FILES:
                destination = archive_destination(root, item, stamp)
                actions.append(CleanAction("move", name, relpath(destination, root), "deprecated-root-file"))
            elif not name.startswith("."):
                destination = archive_destination(root, item, stamp)
                actions.append(CleanAction("move", name, relpath(destination, root), "local-root-file"))
            continue
        if item.is_dir():
            if name in ALLOWED_ROOT_DIRS:
                continue
            if name.startswith("."):
                continue
            destination = archive_destination(root, item, stamp)
            actions.append(CleanAction("move", name, relpath(destination, root), "unknown-root-dir"))

    return actions


def apply_actions(root: Path, actions: list[CleanAction]) -> None:
    for action in actions:
        source = root / action.path
        if action.action == "move":
            move_path(source, root / action.destination, apply=True)
        elif action.action in {"remove_file", "remove_empty_dir"} and source.exists():
            remove_path(source, apply=True)


def clean_root(root: Path = ROOT, *, apply: bool = False, stamp: str | None = None) -> list[CleanAction]:
    resolved_root = root.resolve()
    actions = root_actions(resolved_root, stamp=timestamp_value(stamp))
    if apply:
        apply_actions(resolved_root, actions)
    return actions


def print_human(actions: list[CleanAction], *, apply: bool) -> None:
    mode = "APPLY" if apply else "DRY RUN"
    print(f"{mode}: {len(actions)} root cleanup action(s)")
    for action in actions:
        if action.destination:
            print(f"- {action.action}: {action.path} -> {action.destination} ({action.reason})")
        else:
            print(f"- {action.action}: {action.path} ({action.reason})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview actions without changing files")
    mode.add_argument("--apply", action="store_true", help="Move/prune local root clutter")
    parser.add_argument("--root", default=str(ROOT), help="Repo root to clean")
    parser.add_argument("--timestamp", default=None, help="Deterministic archive timestamp for tests")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    apply = bool(args.apply)
    actions = clean_root(Path(args.root), apply=apply, stamp=args.timestamp)
    payload = {
        "mode": "apply" if apply else "dry-run",
        "actions": [asdict(action) for action in actions],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(actions, apply=apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
