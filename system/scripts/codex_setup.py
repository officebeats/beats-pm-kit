"""
Explicit Codex setup for Beats PM Kit.

Unlike `codex_doctor.py`, this script mutates local adapter outputs and the
user's Codex skill directory by design.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.stdio import force_utf8_stdio

force_utf8_stdio()


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Set up Codex adapters and skills")
    parser.add_argument(
        "--skip-user-home",
        action="store_true",
        help="Only sync project-local Codex skills under .codex/skills.",
    )
    parser.add_argument(
        "--skip-hooks",
        action="store_true",
        help="Do not install repository git hooks.",
    )
    args = parser.parse_args(argv)

    run([sys.executable, "system/scripts/sync_cli_adapters.py"])
    run([
        sys.executable,
        "system/scripts/sync_codex_skill_adapters.py",
        "--output-dir",
        str(ROOT / ".codex" / "skills"),
    ])
    if not args.skip_user_home:
        run([sys.executable, "system/scripts/sync_codex_skill_adapters.py"])
    if not args.skip_hooks:
        run([sys.executable, "system/scripts/install_git_hooks.py"])

    print("")
    print("Codex setup complete.")
    print("Optional Docs MCP: https://developers.openai.com/learn/docs-mcp")
    print("Run `python system/scripts/beats.py codex-doctor` to verify.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
