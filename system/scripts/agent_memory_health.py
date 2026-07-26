#!/usr/bin/env python3
"""Check local read-only agent memory and graph availability."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts import personal_memory


@dataclass
class AgentMemoryHealth:
    configured: bool
    available: bool
    status: str
    memory_path: str
    graph_path: str
    fallback: str
    read_only: bool
    issues: list[str]
    companion: dict


def health_status(root: Path | str | None = None) -> AgentMemoryHealth:
    repo_root = Path(root) if root is not None else ROOT
    memory_path = repo_root / "SESSION_MEMORY.md"
    graph_path = repo_root / ".beats" / "memory" / "symbolic_graph.mermaid"
    legacy_graph_path = repo_root / ".agent" / "memory" / "symbolic_graph.mermaid"
    script_path = repo_root / "system" / "scripts" / "agentic_memory.py"
    issues: list[str] = []

    if not graph_path.exists() and legacy_graph_path.exists():
        graph_path = legacy_graph_path
        issues.append(
            "Using the legacy .agent/memory graph path; the current local engine writes under .beats/memory."
        )

    configured = script_path.exists() or memory_path.exists() or graph_path.exists()
    available = memory_path.exists() or graph_path.exists()

    if not script_path.exists():
        issues.append("Missing system/scripts/agentic_memory.py.")
    if not available:
        issues.append("No SESSION_MEMORY.md or symbolic graph file found; use repo-local rg fallback.")

    if available:
        status = "healthy"
        fallback = "none"
    elif configured:
        status = "degraded"
        fallback = "rg"
    else:
        status = "missing_config"
        fallback = "rg"

    try:
        companion = personal_memory.status(root=repo_root)
    except ValueError as exc:
        companion = {
            "status": "invalid_config",
            "enabled": False,
            "capture_enabled": False,
            "fallback": "rg",
            "issue": str(exc),
        }
        issues.append("Invalid .beats/personal-memory.json; companion stays disabled.")

    return AgentMemoryHealth(
        configured=configured,
        available=available,
        status=status,
        memory_path=str(memory_path),
        graph_path=str(graph_path),
        fallback=fallback,
        read_only=True,
        issues=issues,
        companion=companion,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asdict(health_status(args.root)), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
