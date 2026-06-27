#!/usr/bin/env python3
"""Run realistic Beats PM Kit use-case tests for release and CI gates."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CI_MODULES = [
    "system.tests.test_bootstrap",
    "system.tests.test_root_cleaner",
    "system.tests.test_pm_decision_router",
    "system.tests.test_task_master_triage_real_use",
    "system.tests.test_transcript_pipeline",
    "system.tests.test_obsidian_vault_setup",
    "system.tests.test_obsidian_mcp_health",
    "system.tests.test_agent_memory_health",
    "system.tests.test_adapter_guard",
    "system.tests.test_privacy_guard",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci", action="store_true", help="Run the CI real-use gate")
    parser.add_argument(
        "--update-golden",
        action="store_true",
        help="Reserved for intentional fixture updates; CI must not use this",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.ci and args.update_golden:
        print("--update-golden is not allowed with --ci", file=sys.stderr)
        return 2

    modules = CI_MODULES
    cmd = [sys.executable, "-B", "-m", "unittest", *modules, "-v"]
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode == 0:
        print("Real-use scenario gate passed.")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
