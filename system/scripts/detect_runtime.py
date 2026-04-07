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


def detect_runtime():
    """Detect which AI runtime is active and return its capabilities."""
    root = Path(__file__).resolve().parent.parent.parent
    runtimes = []

    # Antigravity
    if os.environ.get("ANTIGRAVITY_ROOT") or (root / ".agent").is_dir():
        runtimes.append({
            "name": "antigravity",
            "display": "Google Antigravity",
            "detected_by": "env:ANTIGRAVITY_ROOT" if os.environ.get("ANTIGRAVITY_ROOT") else ".agent/ directory",
            "capabilities": ["parallel_fan_out", "mcp_tools", "browser_agent", "native_clipboard", "pencil_design"],
            "config_dir": ".agent/",
            "rules_file": ".agent/rules/GEMINI.md",
            "priority": 1
        })

    # Gemini CLI
    if shutil.which("gemini") or (root / ".gemini").is_dir():
        runtimes.append({
            "name": "gemini_cli",
            "display": "Gemini CLI",
            "detected_by": "binary:gemini" if shutil.which("gemini") else ".gemini/ directory",
            "capabilities": ["sequential_tools", "file_access", "web_search"],
            "config_dir": ".gemini/",
            "rules_file": ".gemini/GEMINI.md",
            "priority": 2
        })

    # Claude Code
    if shutil.which("claude") or (root / ".claude").is_dir():
        runtimes.append({
            "name": "claude_code",
            "display": "Claude Code",
            "detected_by": "binary:claude" if shutil.which("claude") else ".claude/ directory",
            "capabilities": ["sequential_tools", "file_access", "xml_output", "subagents"],
            "config_dir": ".claude/",
            "rules_file": ".claude/CLAUDE.md",
            "priority": 3
        })

    # KiloCode
    if (root / ".kilocode").is_dir():
        runtimes.append({
            "name": "kilocode",
            "display": "KiloCode CLI",
            "detected_by": ".kilocode/ directory",
            "capabilities": ["sequential_tools", "file_access"],
            "config_dir": ".kilocode/",
            "rules_file": ".kilocode/rules.md",
            "priority": 4
        })

    # Determine primary
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
            print(f"   Also found: {r['display']} ({r['detected_by']})")
    elif result['count'] == 0:
        print("   ⚠️  No AI runtimes detected. Install Antigravity, Gemini CLI, or Claude Code.")
    print()


if __name__ == "__main__":
    result = detect_runtime()
    if "--human" in sys.argv:
        print_human(result)
    else:
        print(json.dumps(result, indent=2))
