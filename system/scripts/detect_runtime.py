#!/usr/bin/env python3
"""Detect the active AI runtime through versioned, fail-closed probes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.stdio import force_utf8_stdio

force_utf8_stdio()

PROBE_SCHEMA_VERSION = 1
RUNTIME_SCHEMA_VERSION = 2
SUPPORTED_PROFILES = ("fast", "balanced", "deep")

RUNTIME_SPECS = (
    {
        "name": "antigravity",
        "display": "Antigravity",
        "binary": "antigravity",
        "env": ("ANTIGRAVITY_ROOT",),
        "config_dir": ".agent",
        "rules_file": ".agent/rules/GEMINI.md",
        "capabilities": (
            "filesystem_read",
            "filesystem_write",
            "command_execution",
            "structured_output",
            "browser",
            "connectors",
            "subagents",
            "parallelism",
        ),
    },
    {
        "name": "claude",
        "display": "Claude Code",
        "binary": "claude",
        "env": ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"),
        "config_dir": ".claude",
        "rules_file": ".claude/CLAUDE.md",
        "capabilities": (
            "filesystem_read",
            "filesystem_write",
            "command_execution",
            "structured_output",
            "subagents",
        ),
    },
    {
        "name": "codex",
        "display": "OpenAI Codex",
        "binary": "codex",
        "env": ("CODEX_SHELL", "CODEX_THREAD_ID", "CODEX_CI"),
        "config_dir": ".codex",
        "rules_file": "AGENTS.md",
        "capabilities": (
            "filesystem_read",
            "filesystem_write",
            "command_execution",
            "structured_output",
            "subagents",
            "parallelism",
        ),
    },
    {
        "name": "gemini",
        "display": "Gemini CLI",
        "binary": "gemini",
        "env": ("GEMINI_CLI",),
        "config_dir": ".gemini",
        "rules_file": ".gemini/GEMINI.md",
        "capabilities": (
            "filesystem_read",
            "filesystem_write",
            "command_execution",
            "structured_output",
            "web_search",
        ),
    },
    {
        "name": "kilocode",
        "display": "KiloCode",
        "binary": "kilocode",
        "env": ("KILOCODE",),
        "config_dir": ".kilocode",
        "rules_file": ".kilocode/rules.md",
        "capabilities": (
            "filesystem_read",
            "filesystem_write",
            "command_execution",
            "structured_output",
        ),
    },
)


def _probe_version(command: str) -> str | None:
    """Return one bounded version line without invoking a shell."""
    try:
        result = subprocess.run(
            [command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0][:200] if result.returncode == 0 and output else None


def _active_marker(spec: dict, env: Mapping[str, str]) -> str | None:
    for name in spec["env"]:
        if env.get(name):
            return f"env:{name}"
    return None


def detect_runtime(
    *,
    root: Path = ROOT,
    env: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
    version_probe: Callable[[str], str | None] = _probe_version,
) -> dict:
    """Detect active and available runtimes without applying brand priority."""
    environment = os.environ if env is None else env
    runtimes: list[dict] = []

    for spec in RUNTIME_SPECS:
        active_marker = _active_marker(spec, environment)
        binary_path = which(spec["binary"])
        config_present = (root / spec["config_dir"]).is_dir()
        if not active_marker and not binary_path and not config_present:
            continue
        version = version_probe(binary_path) if binary_path else None
        available = bool(active_marker or version)
        if active_marker:
            detected_by = active_marker
        elif binary_path:
            detected_by = f"binary:{spec['binary']}"
        else:
            detected_by = f"config:{spec['config_dir']}"
        runtimes.append(
            {
                "name": spec["name"],
                "display": spec["display"],
                "active": bool(active_marker),
                "available": available,
                "adapter_present": config_present,
                "detected_by": detected_by,
                "version": version,
                "capabilities": list(spec["capabilities"]) if available else [],
                "supported_profiles": list(SUPPORTED_PROFILES) if available else [],
                "config_dir": spec["config_dir"] + "/",
                "rules_file": spec["rules_file"],
                "probe": {
                    "schema_version": PROBE_SCHEMA_VERSION,
                    "command": [spec["binary"], "--version"],
                },
            }
        )

    runtimes.sort(key=lambda item: item["name"])
    active = [item for item in runtimes if item["active"]]
    primary = active[0] if len(active) == 1 else None
    selection_status = "active" if primary else "ambiguous" if len(active) > 1 else "none"
    return {
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "probe_schema_version": PROBE_SCHEMA_VERSION,
        "selection_policy": "active-runtime",
        "selection_status": selection_status,
        "primary": primary["name"] if primary else "unknown",
        "primary_display": primary["display"] if primary else "No unambiguous active runtime",
        "primary_version": primary["version"] if primary else None,
        "capabilities": list(primary["capabilities"]) if primary else [],
        "supported_profiles": list(primary["supported_profiles"]) if primary else [],
        "all_runtimes": [item["name"] for item in runtimes],
        "available_runtimes": [item["name"] for item in runtimes if item["available"]],
        "active_runtimes": [item["name"] for item in active],
        "active_count": len(active),
        "count": len(runtimes),
        "details": runtimes,
    }


def capability_supported(result: Mapping[str, object], capability: str) -> bool:
    """Deny capabilities that were not positively reported by the active probe."""
    capabilities = result.get("capabilities", [])
    return isinstance(capabilities, list) and capability in capabilities


def print_human(result: dict) -> None:
    """Print a concise runtime status report."""
    print("Runtime detection")
    print(f"- Selection: {result['selection_status']}")
    print(f"- Primary: {result['primary_display']}")
    if result["primary_version"]:
        print(f"- Version: {result['primary_version']}")
    print(f"- Profiles: {', '.join(result['supported_profiles']) or 'none (fail closed)'}")
    print(f"- Capabilities: {', '.join(result['capabilities']) or 'none (fail closed)'}")
    for runtime in result["details"]:
        state = (
            "active"
            if runtime["active"]
            else "available"
            if runtime["available"]
            else "adapter only"
        )
        version = f"; {runtime['version']}" if runtime["version"] else ""
        print(f"- {runtime['display']}: {state}; {runtime['detected_by']}{version}")


def main(argv: list[str] | None = None) -> int:
    result = detect_runtime()
    if argv is None:
        argv = sys.argv[1:]
    if "--human" in argv:
        print_human(result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
