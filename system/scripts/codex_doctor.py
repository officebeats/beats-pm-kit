"""
Read-only Codex health check for the Beats PM Kit.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

import detect_runtime
import sync_codex_skill_adapters
from system.scripts.feature_inventory import collect_inventory
from system.scripts import personal_memory
from system.utils.command_registry import get_promoted_codex_commands
from system.utils.stdio import force_utf8_stdio

force_utf8_stdio()


GENERATED_FILES = [
    "AGENTS.md",
    "CODEX_COMMANDS.md",
    ".codex/rules.md",
]


def _generated_files_present() -> list[str]:
    return [path for path in GENERATED_FILES if (ROOT / path).exists()]


def _status_state() -> dict:
    root_status = ROOT / "STATUS.md"
    tracker_status = ROOT / "5. Trackers" / "STATUS.md"
    return {
        "root_status_exists": root_status.exists(),
        "tracker_status_exists": tracker_status.exists(),
        "usable": root_status.exists() or tracker_status.exists(),
    }


def _skill_visibility() -> dict:
    expected = {
        command["codex_skill_name"]
        for command in get_promoted_codex_commands(ROOT)
    }
    project_dir = ROOT / ".codex" / "skills"
    project = {
        path.name
        for path in project_dir.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    } if project_dir.is_dir() else set()

    with tempfile.TemporaryDirectory() as tmpdir:
        generated = set(sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT))

    return {
        "expected_count": len(expected),
        "temp_generation_count": len(generated),
        "project_visible_count": len(expected & project),
        "missing_project_skills": sorted(expected - project),
    }


def run_checks() -> dict:
    runtime = detect_runtime.detect_runtime()
    inventory = collect_inventory(ROOT)
    status = _status_state()
    skills = _skill_visibility()
    generated_present = _generated_files_present()
    try:
        memory = personal_memory.status(root=ROOT)
    except ValueError as exc:
        memory = {
            "status": "invalid_config",
            "enabled": False,
            "capture_enabled": False,
            "fallback": "rg",
            "issue": str(exc),
        }

    checks = {
        "runtime": runtime,
        "inventory": inventory,
        "generated_files_present": generated_present,
        "missing_generated_files": sorted(set(GENERATED_FILES) - set(generated_present)),
        "status": status,
        "skills": skills,
        "personal_memory": memory,
        "utf8_stdout": (sys.stdout.encoding or "").lower() == "utf-8",
    }
    checks["ok"] = (
        runtime["primary"] == "codex"
        and not checks["missing_generated_files"]
        and skills["temp_generation_count"] == skills["expected_count"]
        and checks["utf8_stdout"]
    )
    return checks


def print_human(result: dict) -> None:
    ok_text = "OK" if result["ok"] else "NEEDS ATTENTION"
    print(f"Codex doctor: {ok_text}")
    print(f"  Runtime: {result['runtime']['primary_display']}")
    print(f"  Workflows: {result['inventory']['workflows']['count']}")
    print(f"  Public skills: {result['inventory']['skills']['count']}")
    print(f"  Promoted Codex commands: {result['inventory']['codex']['promoted_skill_commands_count']}")
    print(f"  Generated files present: {len(result['generated_files_present'])}/{len(GENERATED_FILES)}")
    print(f"  Status file usable: {result['status']['usable']}")
    print(
        "  Personal memory: "
        f"{result['personal_memory']['status']} "
        f"(fallback={result['personal_memory'].get('fallback', 'rg')})"
    )
    print(f"  UTF-8 stdout: {result['utf8_stdout']}")
    if result["skills"]["missing_project_skills"]:
        print("  Project skill adapters missing; run `python system/scripts/beats.py codex-setup`.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Codex health check")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)
    result = run_checks()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
