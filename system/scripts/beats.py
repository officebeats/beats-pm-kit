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
    "chat-intake": ["python3", "system/scripts/chat_intake_state.py"],
    "atlassian-context": ["python3", "system/scripts/atlassian_context_state.py"],
    "transcript": ["python3", "system/scripts/transcript_pipeline.py"],
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


def collect_extra_args(args):
    """Support both legacy --args and modern `--` passthrough."""
    extra_args = []
    legacy_args = getattr(args, "args", "")
    if legacy_args:
        extra_args.extend(shlex.split(legacy_args))
    passthrough = list(getattr(args, "passthrough", []) or [])
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]
    extra_args.extend(passthrough)
    return extra_args


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
    parser.add_argument(
        "passthrough",
        nargs=argparse.REMAINDER,
        help="Additional script args after --, e.g. beats.py teams -- --json",
    )
    args = parser.parse_args()

    if args.command == "resolve":
        workflow_path = resolve_workflow(args.args)
        if workflow_path is None:
            print(f"Unknown workflow: {args.args or '(missing)'}")
            return 1
        print(workflow_path.relative_to(ROOT))
        return 0

    if args.command == "transcript":
        command_config = SCRIPT_COMMANDS[args.command]
        extra_args = collect_extra_args(args)
        if extra_args and extra_args[0] in {"-h", "--help"}:
            return run_cmd(command_config + extra_args)
        if extra_args and extra_args[0] in {"prepare", "validate", "recent"}:
            return run_cmd(command_config + extra_args)
        return run_cmd(command_config + ["prepare"] + extra_args)

    if args.command in WORKFLOW_HINTS:
        print_workflow_hint(args.command)
        return 0

    command_config = SCRIPT_COMMANDS[args.command]
    extra_args = collect_extra_args(args)

    full_cmd = command_config + extra_args
    return run_cmd(full_cmd)


if __name__ == "__main__":
    sys.exit(main())
