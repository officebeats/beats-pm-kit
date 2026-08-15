#!/usr/bin/env python3
"""Report the public Beats PM Kit feature inventory.

The README and release checks use this script so public feature claims stay tied
to the canonical `.agent/` source of truth instead of hand-maintained counts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
AGENT_DIR = ROOT_DIR / ".agent"
COMMAND_REGISTRY_PATH = AGENT_DIR / "command-registry.json"

RUNTIME_DISPLAY_NAMES = {
    "antigravity": "Antigravity",
    "codex": "Codex",
    "gemini": "Gemini CLI",
    "claude": "Claude Code",
    "kilocode": "KiloCode",
}


def _visible_paths(paths: list[Path], cwd: Path) -> list[Path]:
    """Drop git-ignored paths so local-only content never enters public inventory.

    Outside a git checkout (or when git is unavailable) every path is kept.
    """
    if not paths:
        return []
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "--stdin", "-z"],
            cwd=cwd,
            input=b"\x00".join(bytes(p) for p in paths) + b"\x00",
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return paths
    if proc.returncode not in (0, 1):
        return paths
    ignored = set(proc.stdout.split(b"\x00")) - {b""}
    return [path for path in paths if bytes(path) not in ignored]


def _names_from_files(path: Path, pattern: str = "*.md") -> list[str]:
    if not path.exists():
        return []
    files = [item for item in path.glob(pattern) if item.is_file()]
    return sorted(item.stem for item in _visible_paths(files, cwd=path))


def _skill_package_names(path: Path) -> list[str]:
    """Return executable skill packages, excluding standalone reference files."""
    if not path.exists():
        return []
    manifests = [
        item / "SKILL.md"
        for item in path.iterdir()
        if item.is_dir() and not item.name.startswith(".") and (item / "SKILL.md").is_file()
    ]
    return sorted(manifest.parent.name for manifest in _visible_paths(manifests, cwd=path))


def _load_command_registry() -> dict[str, Any]:
    if not COMMAND_REGISTRY_PATH.exists():
        return {}
    return json.loads(COMMAND_REGISTRY_PATH.read_text(encoding="utf-8"))


def _runtime_names(registry: dict[str, Any]) -> list[str]:
    policy = registry.get("runtime_policy", {})
    supported = policy.get("supported", []) if isinstance(policy, dict) else []
    raw = [item for item in supported if isinstance(item, str)]

    seen: set[str] = set()
    runtimes: list[str] = []
    for runtime in raw:
        if runtime == "other-clis" or runtime in seen:
            continue
        seen.add(runtime)
        runtimes.append(RUNTIME_DISPLAY_NAMES.get(runtime, runtime))
    return runtimes


def _promoted_codex_commands(registry: dict[str, Any]) -> list[str]:
    commands = registry.get("commands", {})
    if not isinstance(commands, dict):
        return []
    promoted: list[str] = []
    for command, config in commands.items():
        codex = config.get("codex", {}) if isinstance(config, dict) else {}
        if isinstance(codex, dict) and codex.get("promotion") == "skill":
            promoted.append(command)
    return sorted(promoted)


def collect_inventory(root_dir: Path = ROOT_DIR) -> dict[str, Any]:
    agent_dir = root_dir / ".agent"
    registry = json.loads((agent_dir / "command-registry.json").read_text(encoding="utf-8"))
    agents = _names_from_files(agent_dir / "agents")
    workflows = _names_from_files(agent_dir / "workflows")
    skills = _skill_package_names(agent_dir / "skills")
    promoted_codex_commands = _promoted_codex_commands(registry)
    runtimes = _runtime_names(registry)

    return {
        "source_of_truth": ".agent/",
        "agents": {
            "count": len(agents),
            "names": agents,
        },
        "workflows": {
            "count": len(workflows),
            "names": workflows,
        },
        "skills": {
            "count": len(skills),
            "names": skills,
            "counting_rule": "Directories under .agent/skills that contain SKILL.md",
        },
        "runtimes": {
            "count": len(runtimes),
            "names": runtimes,
        },
        "codex": {
            "promoted_skill_commands_count": len(promoted_codex_commands),
            "promoted_skill_commands": promoted_codex_commands,
        },
        "execution_profiles": registry.get("command_profiles", {}),
    }


def print_markdown(inventory: dict[str, Any]) -> None:
    print("# Feature Inventory")
    print()
    print(f"- Source of truth: `{inventory['source_of_truth']}`")
    print(f"- Agents: {inventory['agents']['count']}")
    print(f"- Workflows: {inventory['workflows']['count']}")
    print(f"- Skills: {inventory['skills']['count']}")
    print(f"- Supported runtimes: {', '.join(inventory['runtimes']['names'])}")
    print(
        "- Promoted Codex skill commands: "
        f"{inventory['codex']['promoted_skill_commands_count']}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--markdown", action="store_true", help="Print a Markdown summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = collect_inventory()
    if args.markdown:
        print_markdown(inventory)
    else:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
