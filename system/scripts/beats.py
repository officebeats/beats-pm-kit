import argparse
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.command_registry import build_command_catalog, resolve_command_name

SCRIPT_COMMANDS = {
    "runtime": ["python3", "system/scripts/detect_runtime.py", "--human"],
    "sync": ["python3", "system/scripts/sync_cli_adapters.py"],
    "codex-skills": ["python3", "system/scripts/sync_codex_skill_adapters.py"],
    "guard": ["python3", "system/scripts/adapter_guard.py", "--mode", "fix"],
    "hooks": ["python3", "system/scripts/install_git_hooks.py"],
    "health": ["python3", "system/scripts/context_health.py"],
    "transcript": [
        ["python3", "system/scripts/quill_mcp_client.py"],
        ["python3", "system/scripts/transcript_fetcher.py"],
        ["python3", "system/scripts/transcript_intake.py"],
    ],
    "outlook": ["python3", "system/scripts/outlook_bridge.py"],
    "teams": ["python3", "system/scripts/teams_bridge.py"],
    "vibe": ["python3", "system/scripts/vibe_check.py"],
    "vacuum": ["python3", "system/scripts/vacuum.py"],
}

WORKFLOW_HINTS = {
    entry["name"]: entry["workflow"] for entry in build_command_catalog(ROOT)
}


def run_cmd(cmd):
    """Run a concrete script command."""
    script_path = ROOT / cmd[1]
    if not script_path.exists():
        print(f"Missing script: {cmd[1]}")
        return 1
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    return result.returncode


def resolve_workflow(command_text):
    """Resolve a slash command or bare workflow name to a workflow file."""
    command = resolve_command_name(command_text, ROOT)
    if command is None:
        return None
    workflow_path = ROOT / ".agent" / "workflows" / f"{command}.md"
    if workflow_path.exists():
        return workflow_path
    return None


def print_workflow_hint(command):
    """Explain how to run model-driven workflows from Codex or Antigravity."""
    workflow_path = WORKFLOW_HINTS[command]
    print(f"`{command}` is a model-driven workflow, not a standalone Python script.")
    print(f"Run it from your AI runtime by loading `{workflow_path}`.")
    print("")
    print("Examples:")
    print(f'- Codex: "Run `/{command}` by reading `{workflow_path}` and the minimum required skills."')
    print(f'- Antigravity: "/{command}"')


def main():
    parser = argparse.ArgumentParser(description="Beats PM Kit - Universal CLI Gateway")
    parser.add_argument(
        "command",
        choices=sorted(set(SCRIPT_COMMANDS) | set(WORKFLOW_HINTS) | {"resolve"}),
        help="Script-backed utility or workflow hint",
    )
    parser.add_argument("--args", help="Additional arguments for script-backed commands", default="")
    args = parser.parse_args()

    if args.command == "resolve":
        workflow_path = resolve_workflow(args.args)
        if workflow_path is None:
            print(f"Unknown workflow: {args.args or '(missing)'}")
            return 1
        print(workflow_path.relative_to(ROOT))
        return 0

    if args.command in WORKFLOW_HINTS:
        print_workflow_hint(args.command)
        return 0

    command_config = SCRIPT_COMMANDS[args.command]
    extra_args = shlex.split(args.args)

    if args.command == "transcript":
        exit_code = 0
        for cmd in command_config:
            full_cmd = cmd + extra_args
            exit_code = run_cmd(full_cmd)
            if exit_code != 0:
                return exit_code
        return exit_code

    full_cmd = command_config + extra_args
    return run_cmd(full_cmd)


if __name__ == "__main__":
    sys.exit(main())
