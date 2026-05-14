"""
Authoritative public inventory for Beats PM Kit docs and guards.

This script intentionally counts the public source surfaces, not transient
generated mirrors. In particular, `source-command-*` skill mirrors are excluded
from the public skill count.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.command_registry import build_command_catalog, get_runtime_priority
from system.utils.stdio import force_utf8_stdio

force_utf8_stdio()


def _names_from_files(path: Path, suffix: str) -> list[str]:
    if not path.is_dir():
        return []
    return sorted(
        item.stem
        for item in path.iterdir()
        if item.name.endswith(suffix) and not item.name.startswith(".")
    )


def _public_skill_names(path: Path) -> list[str]:
    if not path.is_dir():
        return []
    names = []
    for item in path.iterdir():
        if (
            item.is_dir()
            and not item.name.startswith("source-command-")
            and (item / "SKILL.md").exists()
        ):
            names.append(item.name)
    return sorted(names)


def build_inventory(root: Path = ROOT) -> dict:
    catalog = build_command_catalog(root)
    priority = get_runtime_priority(root)
    promoted = [entry for entry in catalog if entry["codex_promotion"] == "skill"]
    runtimes = [
        priority["primary"],
        priority["secondary"],
        *[
            runtime
            for runtime in priority.get("compatibility", [])
            if runtime != "other-clis"
        ],
    ]

    agents = _names_from_files(root / ".agent" / "agents", ".md")
    skills = _public_skill_names(root / ".agent" / "skills")
    workflows = [entry["name"] for entry in catalog]

    return {
        "agents": {"count": len(agents), "names": agents},
        "skills": {"count": len(skills), "names": skills},
        "workflows": {"count": len(workflows), "names": workflows},
        "runtimes": {"count": len(runtimes), "names": runtimes, "priority": priority},
        "codex": {
            "promoted_skill_commands_count": len(promoted),
            "promoted_skill_commands": [entry["name"] for entry in promoted],
            "promoted_skill_names": [entry["codex_skill_name"] for entry in promoted],
        },
    }


def print_human(inventory: dict) -> None:
    print("Beats PM Kit inventory")
    print(f"  Agents: {inventory['agents']['count']}")
    print(f"  Workflows: {inventory['workflows']['count']}")
    print(f"  Public skills: {inventory['skills']['count']}")
    print(f"  Runtimes: {', '.join(inventory['runtimes']['names'])}")
    print(f"  Promoted Codex commands: {inventory['codex']['promoted_skill_commands_count']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print Beats PM Kit feature inventory")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    inventory = build_inventory()
    if args.json:
        print(json.dumps(inventory, indent=2))
    else:
        print_human(inventory)
    return 0


if __name__ == "__main__":
    sys.exit(main())
