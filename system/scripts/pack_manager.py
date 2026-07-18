#!/usr/bin/env python3
"""Enable and run optional Beats PM packs stored in this repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKS_DIR = Path("packs")
CONFIG_PATH = Path(".beats/packs.json")


@dataclass(frozen=True)
class Pack:
    pack_id: str
    title: str
    description: str
    version: str
    entrypoint: str
    runner: str
    triggers: tuple[str, ...]
    path: Path


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def discover(root: Path = ROOT) -> dict[str, Pack]:
    packs: dict[str, Pack] = {}
    base = root / PACKS_DIR
    if not base.exists():
        return packs
    for manifest_path in sorted(base.glob("*/pack.json")):
        data = _read_json(manifest_path, {})
        pack_id = str(data.get("id") or "").strip()
        title = str(data.get("title") or "").strip()
        entrypoint = str(data.get("entrypoint") or "PACK.md").strip()
        if not pack_id or not title or pack_id in packs:
            continue
        packs[pack_id] = Pack(
            pack_id=pack_id,
            title=title,
            description=str(data.get("description") or "").strip(),
            version=str(data.get("version") or "").strip(),
            entrypoint=entrypoint,
            runner=str(data.get("runner") or "").strip(),
            triggers=tuple(str(item) for item in data.get("triggers", []) if str(item).strip()),
            path=manifest_path.parent,
        )
    return packs


def enabled_ids(root: Path = ROOT) -> list[str]:
    data = _read_json(root / CONFIG_PATH, {"enabled": []})
    return sorted({str(item) for item in data.get("enabled", []) if str(item).strip()})


def save_enabled(root: Path, values: list[str]) -> Path:
    path = root / CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "enabled": sorted(set(values))}, indent=2) + "\n", encoding="utf-8")
    return path


def pack_rows(root: Path = ROOT) -> list[dict[str, Any]]:
    active = set(enabled_ids(root))
    return [
        {
            "id": pack.pack_id,
            "title": pack.title,
            "description": pack.description,
            "version": pack.version,
            "enabled": pack.pack_id in active,
            "entrypoint": str(pack.path.joinpath(pack.entrypoint).relative_to(root)),
        }
        for pack in discover(root).values()
    ]


def set_enabled(root: Path, pack_id: str, enabled: bool) -> dict[str, Any]:
    packs = discover(root)
    if pack_id not in packs:
        raise ValueError(f"Unknown pack: {pack_id}")
    active = set(enabled_ids(root))
    if enabled:
        active.add(pack_id)
    else:
        active.discard(pack_id)
    path = save_enabled(root, sorted(active))
    return {"id": pack_id, "enabled": enabled, "config": path.relative_to(root).as_posix()}


def run_pack(root: Path, pack_id: str, args: list[str]) -> int:
    packs = discover(root)
    pack = packs.get(pack_id)
    if pack is None:
        raise ValueError(f"Unknown pack: {pack_id}")
    if pack_id not in enabled_ids(root):
        raise ValueError(f"Pack '{pack_id}' is disabled. Enable it with: /pack enable {pack_id}")
    if not pack.runner:
        raise ValueError(f"Pack '{pack_id}' does not provide a script runner")
    runner = (root / pack.runner).resolve()
    if root.resolve() not in runner.parents or not runner.is_file():
        raise ValueError(f"Pack '{pack_id}' runner is missing or outside the kit")
    return subprocess.run([sys.executable, str(runner), *args], cwd=root, check=False).returncode


def _emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    if isinstance(data, list):
        if not data:
            print("No packs found.")
            return
        for item in data:
            state = "enabled" if item["enabled"] else "disabled"
            print(f"- {item['title']} ({item['id']}): {state} — {item['description']}")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List available packs")
    status = commands.add_parser("status", help="Show one pack or all packs")
    status.add_argument("pack_id", nargs="?")
    enable = commands.add_parser("enable", help="Enable a local pack")
    enable.add_argument("pack_id")
    disable = commands.add_parser("disable", help="Disable a local pack")
    disable.add_argument("pack_id")
    run = commands.add_parser("run", help="Run an enabled pack's script")
    run.add_argument("pack_id")
    run.add_argument("args", nargs=argparse.REMAINDER)
    parsed = parser.parse_args(argv)
    root = parsed.root.resolve()

    try:
        if parsed.command == "list":
            _emit(pack_rows(root), parsed.json)
            return 0
        if parsed.command == "status":
            rows = pack_rows(root)
            if parsed.pack_id:
                rows = [row for row in rows if row["id"] == parsed.pack_id]
                if not rows:
                    raise ValueError(f"Unknown pack: {parsed.pack_id}")
            _emit(rows, parsed.json)
            return 0
        if parsed.command in {"enable", "disable"}:
            result = set_enabled(root, parsed.pack_id, parsed.command == "enable")
            _emit(result, parsed.json)
            return 0
        if parsed.command == "run":
            passthrough = parsed.args[1:] if parsed.args[:1] == ["--"] else parsed.args
            return run_pack(root, parsed.pack_id, passthrough)
    except ValueError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
