"""
Runtime Detection Script
Detects which AI CLI environment is active and returns capabilities.

Usage:
    python3 system/scripts/detect_runtime.py          # JSON output
    python3 system/scripts/detect_runtime.py --human   # Human-readable output
"""

import json
import os
import shutil
import sys
from pathlib import Path


def _has_env(*names):
    """Return True when any listed environment variable is set."""
    return any(os.environ.get(name) for name in names)


def detect_runtime():
    """Detect which AI runtime is active and return its capabilities."""
    root = Path(__file__).resolve().parent.parent.parent
    runtimes = []

    # Antigravity
    antigravity_active = _has_env("ANTIGRAVITY_ROOT")
    if antigravity_active or (root / ".agent").is_dir():
        runtimes.append({
            "name": "antigravity",
            "display": "Google Antigravity",
            "detected_by": "env:ANTIGRAVITY_ROOT" if antigravity_active else ".agent/ directory",
            "capabilities": ["parallel_fan_out", "mcp_tools", "browser_agent", "native_clipboard", "pencil_design"],
            "config_dir": ".agent/",
            "rules_file": ".agent/rules/GEMINI.md",
            "priority": 10 if antigravity_active else 90,
            "active": antigravity_active
        })

    # Gemini CLI
    gemini_active = _has_env("GEMINI_CLI")
    if gemini_active or shutil.which("gemini") or (root / ".gemini").is_dir():
        runtimes.append({
            "name": "gemini_cli",
            "display": "Gemini CLI",
            "detected_by": (
                "env:GEMINI_CLI" if gemini_active else
                "binary:gemini" if shutil.which("gemini") else
                ".gemini/ directory"
            ),
            "capabilities": ["sequential_tools", "file_access", "web_search"],
            "config_dir": ".gemini/",
            "rules_file": ".gemini/GEMINI.md",
            "priority": 20 if gemini_active else 60,
            "active": gemini_active
        })

    # Claude Code
    claude_active = _has_env("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")
    if claude_active or shutil.which("claude") or (root / ".claude").is_dir():
        runtimes.append({
            "name": "claude_code",
            "display": "Claude Code",
            "detected_by": (
                "env:CLAUDECODE" if claude_active else
                "binary:claude" if shutil.which("claude") else
                ".claude/ directory"
            ),
            "capabilities": ["sequential_tools", "file_access", "xml_output", "subagents"],
            "config_dir": ".claude/",
            "rules_file": ".claude/CLAUDE.md",
            "priority": 30 if claude_active else 70,
            "active": claude_active
        })


    # OpenAI Codex CLI
    codex_active = _has_env("CODEX_SHELL", "CODEX_THREAD_ID", "CODEX_CI")
    if codex_active or shutil.which("codex") or (root / ".codex").is_dir():
        runtimes.append({
            "name": "codex_cli",
            "display": "OpenAI Codex CLI",
            "detected_by": (
                "env:CODEX_SHELL" if codex_active else
                "binary:codex" if shutil.which("codex") else
                ".codex/ directory"
            ),
            "capabilities": ["sequential_tools", "file_access", "code_execution"],
            "config_dir": ".codex/",
            "rules_file": "AGENTS.md",
            "priority": 40 if codex_active else 50,
            "active": codex_active
        })

    # KiloCode
    kilocode_active = _has_env("KILOCODE")
    if kilocode_active or (root / ".kilocode").is_dir():
        runtimes.append({
            "name": "kilocode",
            "display": "KiloCode CLI",
            "detected_by": "env:KILOCODE" if kilocode_active else ".kilocode/ directory",
            "capabilities": ["sequential_tools", "file_access"],
            "config_dir": ".kilocode/",
            "rules_file": ".kilocode/rules.md",
            "priority": 50 if kilocode_active else 80,
            "active": kilocode_active
        })

    # Determine primary
    runtimes.sort(key=lambda runtime: runtime["priority"])
    primary = runtimes[0] if runtimes else None

    return {
        "primary": primary["name"] if primary else "unknown",
        "primary_display": primary["display"] if primary else "No AI runtime detected",
        "capabilities": primary["capabilities"] if primary else [],
        "all_runtimes": [r["name"] for r in runtimes],
        "count": len(runtimes),
        "details": runtimes
    }


def print_human(result):
    """Print detection results in human-readable format."""
    print(f"\n🔍 Runtime Detection")
    print(f"   Primary: {result['primary_display']}")
    print(f"   Capabilities: {', '.join(result['capabilities'])}")
    if result['count'] > 1:
        others = [r for r in result['details'] if r['name'] != result['primary']]
        for r in others:
            qualifier = "active" if r.get("active") else "available"
            print(f"   Also found: {r['display']} ({qualifier}; {r['detected_by']})")
    elif result['count'] == 0:
        print("   ⚠️  No AI runtimes detected. Install Antigravity, Gemini CLI, Claude Code, or Codex CLI.")
    print()


if __name__ == "__main__":
    result = detect_runtime()
    if "--human" in sys.argv:
        print_human(result)
    else:
        print(json.dumps(result, indent=2))
