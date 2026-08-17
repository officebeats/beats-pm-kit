"""
Shared command registry helpers for cross-runtime workflow adapters.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_DIR = ROOT_DIR / ".agent"
REGISTRY_PATH = CANONICAL_DIR / "command-registry.json"
DESCRIPTION_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
MULTILINE_MARKERS = {"|-", "|", ">-", ">", "|+", ">+"}

SCHEMA_VERSION = 3
PROFILE_NAMES = ("fast", "balanced", "deep")
RESPONSE_PROFILES = ("compact_operator", "artifact", "verbatim")


def get_root(root: Path | str | None = None) -> Path:
    """Return the repo root used for registry and workflow lookups."""
    return Path(root) if root is not None else ROOT_DIR


def get_registry_path(root: Path | str | None = None) -> Path:
    """Return the command registry path."""
    return get_root(root) / ".agent" / "command-registry.json"


def normalize_command_name(text: str) -> str:
    """Normalize a slash command or alias down to its first token."""
    stripped = text.strip()
    if not stripped:
        return ""
    token = stripped.split()[0]
    return token.lstrip("/").strip()


def is_git_ignored(path: Path, root: Path) -> bool:
    """Return True when a path is explicitly ignored in this local checkout."""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", str(path.relative_to(root))],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, ValueError):
        return False
    return result.returncode == 0


def get_workflow_descriptions(root: Path | str | None = None):
    """Return workflow names with descriptions parsed from frontmatter."""
    repo_root = get_root(root)
    workflows_dir = repo_root / ".agent" / "workflows"
    workflow_meta = []

    if not workflows_dir.is_dir():
        return workflow_meta

    for path in sorted(workflows_dir.glob("*.md")):
        if is_git_ignored(path, repo_root):
            continue
        description = ""
        text = path.read_text(encoding="utf-8")
        match = DESCRIPTION_RE.search(text)
        if match:
            description = match.group(1).strip().strip('"')
            if description in MULTILINE_MARKERS:
                description = ""
        workflow_meta.append((path.stem, description))

    return workflow_meta


def load_command_registry(root: Path | str | None = None):
    """Load the canonical routing registry."""
    path = get_registry_path(root)
    if not path.exists():
        raise FileNotFoundError(f"Canonical command registry is missing: {path}")
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported command registry schema: {registry.get('schema_version')}; "
            f"expected {SCHEMA_VERSION}"
        )
    return registry


def get_runtime_policy(root: Path | str | None = None):
    """Return the capability-driven runtime policy."""
    policy = load_command_registry(root).get("runtime_policy")
    if not isinstance(policy, dict):
        raise ValueError("Command registry is missing runtime_policy")
    if policy.get("selection") != "active-runtime":
        raise ValueError("runtime_policy.selection must be 'active-runtime'")
    if policy.get("unknown_capabilities") != "deny":
        raise ValueError("runtime_policy.unknown_capabilities must be 'deny'")
    return policy


def get_harness_policy(root: Path | str | None = None):
    """Return the validated runtime-neutral agentic harness contract."""
    policy = load_command_registry(root).get("harness")
    if not isinstance(policy, dict):
        raise ValueError("Command registry is missing harness policy")
    if policy.get("routing", {}).get("strategy") != "one-level":
        raise ValueError("harness.routing.strategy must be 'one-level'")
    if policy.get("primary_runtimes") != ["antigravity", "codex", "claude"]:
        raise ValueError("harness.primary_runtimes must be antigravity, codex, and claude")
    budgets = policy.get("context_budgets")
    required = {
        "runtime_bootstrap_tokens",
        "registry_tokens",
        "skill_entrypoint_tokens",
        "initial_command_tokens",
    }
    if not isinstance(budgets, dict) or not required.issubset(budgets):
        raise ValueError("harness.context_budgets is incomplete")
    if any(not isinstance(budgets[name], int) or budgets[name] <= 0 for name in required):
        raise ValueError("harness context budgets must be positive integers")
    cache_policy = policy.get("cache_policy")
    if not isinstance(cache_policy, dict) or cache_policy.get("deterministic_tool_order") is not True:
        raise ValueError("harness cache policy must require deterministic tool ordering")
    if cache_policy.get("append_dynamic_context_after_prefix") is not True:
        raise ValueError("harness cache policy must keep dynamic context after the stable prefix")
    available = policy.get("response_profiles", {}).get("available")
    if available != list(RESPONSE_PROFILES):
        raise ValueError(
            "harness response profiles must define compact_operator, artifact, and verbatim"
        )
    selection = policy.get("response_profiles", {}).get("selection")
    if not isinstance(selection, dict) or set(selection) != set(RESPONSE_PROFILES):
        raise ValueError("harness response profile selection rules are incomplete")
    if policy.get("optimizer", {}).get("promotion") != "human-approved":
        raise ValueError("harness optimizer promotion must remain human-approved")
    return policy


def get_execution_profiles(root: Path | str | None = None):
    """Return validated abstract execution profiles in escalation order."""
    profiles = load_command_registry(root).get("execution_profiles")
    if not isinstance(profiles, dict) or set(profiles) != set(PROFILE_NAMES):
        raise ValueError("execution_profiles must define fast, balanced, and deep")
    ranks = [profiles[name].get("rank") for name in PROFILE_NAMES]
    if ranks != [1, 2, 3]:
        raise ValueError("execution profile ranks must be fast=1, balanced=2, deep=3")
    return profiles


def get_escalation_signals(root: Path | str | None = None):
    """Return the allowlisted automatic escalation signals."""
    signals = load_command_registry(root).get("escalation_signals")
    if not isinstance(signals, list) or not signals or not all(isinstance(item, str) for item in signals):
        raise ValueError("escalation_signals must be a non-empty string list")
    if len(signals) != len(set(signals)):
        raise ValueError("escalation_signals cannot contain duplicates")
    return tuple(signals)


def get_command_profile_map(root: Path | str | None = None) -> dict[str, str]:
    """Return command-to-profile assignments after strict coverage validation."""
    registry = load_command_registry(root)
    profiles = get_execution_profiles(root)
    assignments = registry.get("command_profiles")
    if not isinstance(assignments, dict) or set(assignments) != set(profiles):
        raise ValueError("command_profiles must define fast, balanced, and deep")

    owners: dict[str, str] = {}
    duplicates: set[str] = set()
    for profile in PROFILE_NAMES:
        commands = assignments.get(profile)
        if not isinstance(commands, list) or not all(isinstance(item, str) for item in commands):
            raise ValueError(f"command_profiles.{profile} must be a string list")
        for command in commands:
            if command in owners:
                duplicates.add(command)
            owners[command] = profile
    if duplicates:
        raise ValueError("Commands have multiple execution profiles: " + ", ".join(sorted(duplicates)))
    return owners


def build_command_catalog(root: Path | str | None = None):
    """Merge workflow files with cross-runtime adapter metadata."""
    repo_root = get_root(root)
    workflow_meta = get_workflow_descriptions(repo_root)
    workflow_name_list = [name for name, _ in workflow_meta]
    duplicate_workflows = sorted(
        name for name, count in Counter(workflow_name_list).items() if count > 1
    )
    if duplicate_workflows:
        raise ValueError(
            "Duplicate canonical workflow names found: "
            + ", ".join(f"/{name}" for name in duplicate_workflows)
        )

    normalized_workflow_owners: dict[str, str] = {}
    for name in workflow_name_list:
        normalized_name = normalize_command_name(name)
        owner = normalized_workflow_owners.get(normalized_name)
        if owner is not None and owner != name:
            raise ValueError(
                f"Workflow name '/{name}' normalizes to '/{normalized_name}', "
                f"which already belongs to /{owner}"
            )
        normalized_workflow_owners[normalized_name] = name

    workflow_names = set(workflow_name_list)
    registry = load_command_registry(repo_root)
    get_runtime_policy(repo_root)
    harness = get_harness_policy(repo_root)
    get_escalation_signals(repo_root)
    command_meta = registry.get("commands", {})
    profile_map = get_command_profile_map(repo_root)

    unknown_commands = sorted(set(command_meta) - workflow_names)
    if unknown_commands:
        raise ValueError(
            "Command registry references workflows that do not exist: "
            + ", ".join(unknown_commands)
        )

    missing_profiles = sorted(workflow_names - set(profile_map))
    if missing_profiles:
        raise ValueError("Commands are missing execution profiles: " + ", ".join(missing_profiles))
    unknown_profile_commands = sorted(set(profile_map) - workflow_names)
    if unknown_profile_commands:
        raise ValueError(
            "Execution profiles reference workflows that do not exist: "
            + ", ".join(unknown_profile_commands)
        )

    alias_owners = {}
    codex_skill_owners = {}
    catalog = []

    for name, description in workflow_meta:
        override = command_meta.get(name, {})
        codex = override.get("codex", {})
        promotion = codex.get("promotion", "dispatch-only")
        if promotion not in {"dispatch-only", "skill"}:
            raise ValueError(f"Unsupported Codex promotion mode for /{name}: {promotion}")

        visibility = override.get("visibility", "visible")
        if visibility not in {"visible", "hidden"}:
            raise ValueError(f"Unsupported visibility for /{name}: {visibility}")

        aliases = []
        for alias in override.get("aliases", []):
            normalized = normalize_command_name(alias)
            if not normalized or normalized == name or normalized in aliases:
                continue
            canonical_owner = normalized_workflow_owners.get(normalized)
            if canonical_owner is not None and canonical_owner != name:
                raise ValueError(
                    f"Alias '/{normalized}' for /{name} collides with canonical "
                    f"workflow /{canonical_owner}"
                )
            owner = alias_owners.get(normalized)
            if owner is not None and owner != name:
                raise ValueError(
                    f"Alias '/{normalized}' is assigned to both /{owner} and /{name}"
                )
            alias_owners[normalized] = name
            aliases.append(normalized)

        skill_name = codex.get("skill_name")
        if promotion == "skill" and not skill_name:
            raise ValueError(f"Promoted Codex command /{name} is missing skill_name")
        if skill_name:
            owner = codex_skill_owners.get(skill_name)
            if owner is not None and owner != name:
                raise ValueError(
                    f"Codex skill '{skill_name}' is assigned to both /{owner} and /{name}"
                )
            codex_skill_owners[skill_name] = name

        catalog.append(
            {
                "name": name,
                "workflow": f".agent/workflows/{name}.md",
                "description": description or "See workflow file",
                "execution_profile": profile_map[name],
                "aliases": aliases,
                "dangerous": bool(override.get("dangerous", False)),
                "note": override.get("note", ""),
                "codex_promotion": promotion,
                "visibility": visibility,
                "codex_skill_name": skill_name,
                "codex_supporting_files": codex.get("supporting_files", []),
                "codex_optional_files": codex.get("optional_files", []),
                "codex_execution_contract": codex.get("execution_contract", []),
                "operator_response_profile": harness["response_profiles"]["operator_default"],
                "final_response_profile": override.get(
                    "final_response_profile",
                    harness["response_profiles"]["final_default"],
                ),
                "context_budget_tokens": harness["context_budgets"]["initial_command_tokens"],
                "maximum_initial_sources": harness["routing"]["maximum_initial_sources"],
                "maximum_reference_hops": harness["routing"]["maximum_reference_hops"],
                "supported_runtimes": harness["primary_runtimes"],
                "cache_policy": harness["cache_policy"],
            }
        )

    return catalog


def validate_command_catalog(root: Path | str | None = None):
    """Validate command metadata and return the canonical catalog."""
    return build_command_catalog(root)


def get_promoted_codex_commands(root: Path | str | None = None):
    """Return only commands promoted to Codex skill adapters."""
    return [entry for entry in build_command_catalog(root) if entry["codex_promotion"] == "skill"]


def resolve_command_name(command_text: str, root: Path | str | None = None):
    """Resolve a command or alias to its canonical workflow name."""
    normalized = normalize_command_name(command_text)
    if not normalized:
        return None

    alias_map = {}
    for entry in build_command_catalog(root):
        alias_map[entry["name"]] = entry["name"]
        for alias in entry["aliases"]:
            alias_map[alias] = entry["name"]

    return alias_map.get(normalized)
