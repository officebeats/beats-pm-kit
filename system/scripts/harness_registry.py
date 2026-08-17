#!/usr/bin/env python3
"""Resolve and audit the runtime-neutral Beats Agentic PM Harness registry."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts import harness_telemetry  # noqa: E402
from system.scripts.feature_inventory import _visible_paths as visible_paths  # noqa: E402
from system.utils.command_registry import (  # noqa: E402
    build_command_catalog,
    get_harness_policy,
    resolve_command_name,
)


BOOTSTRAP_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".agent/rules/GEMINI.md",
)


def estimate_tokens(text: str) -> int:
    """Return a stable conservative token estimate without a model dependency."""
    return math.ceil(len(text.encode("utf-8", errors="replace")) / 4)


def compact_discovery_registry(root: Path = ROOT) -> dict[str, Any]:
    """Return the complete one-level ID registry loaded for discovery.

    Rich descriptions stay in the canonical registry and selected entrypoint.
    Discovery only needs stable IDs, aliases, execution profile, and Codex
    promotion status, which prevents every task from paying repeatedly for
    prose it will not use. This is also the exact payload persisted to
    `.agent/command-registry.lite.json` by `render_lite_registry`, so its
    shape is deliberately terse to stay well under the registry token budget:
    `profile` is the execution profile's first letter (f=fast, b=balanced,
    d=deep); `skill` is present (and true) only when the command is promoted
    to a Codex skill adapter, since dispatch-only is the majority case;
    `aliases` is present only when non-empty.
    """
    commands: dict[str, Any] = {}
    for item in build_command_catalog(root):
        entry: dict[str, Any] = {"profile": item["execution_profile"][0]}
        if item["codex_promotion"] == "skill":
            entry["skill"] = True
        if item["aliases"]:
            entry["aliases"] = item["aliases"]
        commands[item["name"]] = entry
    skills = [path.parent.name for path in sorted((root / ".agent" / "skills").glob("*/SKILL.md"))]
    payload = {
        "schema_version": 1,
        "routing": "one-level",
        "commands": commands,
        "skills": skills,
    }
    payload["estimated_tokens"] = estimate_tokens(
        json.dumps(payload, separators=(",", ":"), sort_keys=True)
    )
    return payload


def render_lite_registry(root: Path = ROOT) -> str:
    """Render the persisted `.agent/command-registry.lite.json` contents.

    Uses compact separators (no indentation) deliberately: the whole point of
    this generated file is staying well under the 3KB/registry_tokens budget
    for cold-load discovery, and pretty-printing would roughly double it.
    """
    payload = compact_discovery_registry(root)
    return json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n"


def resolve_harness_command(command: str, root: Path = ROOT) -> dict[str, Any]:
    """Resolve one command into a bounded runtime-neutral execution manifest."""
    canonical = resolve_command_name(command, root)
    if canonical is None:
        raise ValueError(f"Unknown Beats command: {command}")
    entry = next(item for item in build_command_catalog(root) if item["name"] == canonical)
    policy = get_harness_policy(root)
    candidates = list(dict.fromkeys(entry["codex_supporting_files"]))
    optional = list(dict.fromkeys(entry["codex_optional_files"]))
    return {
        "schema_version": 1,
        "kind": "command",
        "id": entry["name"],
        "triggers": [entry["name"], *entry["aliases"]],
        "inputs": ["current user request", "selected workflow sources"],
        "workflow": entry["workflow"],
        "execution_profile": entry["execution_profile"],
        "response": {
            "operator": entry["operator_response_profile"],
            "final": entry["final_response_profile"],
            "verbatim_when": policy["response_profiles"]["selection"]["verbatim"],
        },
        "context": {
            "budget_tokens": entry["context_budget_tokens"],
            "maximum_initial_sources": entry["maximum_initial_sources"],
            "maximum_reference_hops": entry["maximum_reference_hops"],
            "candidate_required": candidates,
            "candidate_optional": optional,
            "instruction": "Read the workflow first, then load only directly relevant candidates; never load this list wholesale.",
            "payload_policy": "Archive full oversized tool results with context_store.py; use compact views in active context and retain deterministic raw retrieval.",
        },
        "permissions": {
            "external_mutation": "explicit-current-turn-authorization",
            "destructive_action": "inspect-target-and-confirm-material-risk",
            "dangerous": entry["dangerous"],
            "note": entry["note"],
        },
        "tools": {
            "selection": "workflow-declared and least-privilege",
            "repo_candidates": [path for path in [*candidates, *optional] if path.endswith(".py")],
        },
        "quality_gate": {
            "no_functionality_regression": True,
            "raw_evidence_authoritative": policy["knowledge"]["raw_evidence_is_authoritative"],
            "execution_contract": entry["codex_execution_contract"],
            "completion_criteria": [
                "workflow intent satisfied",
                "required artifact persisted",
                "source and approval requirements verified",
            ],
        },
        "checkpoint_policy": policy["checkpoint_policy"],
        "cache_policy": entry["cache_policy"],
        "runtimes": {
            "primary": policy["primary_runtimes"],
            "compatibility": policy["compatibility_runtimes"],
        },
        "outputs": {
            "durable": "standard repo folders",
            "trace": policy["telemetry"]["storage"],
        },
        "recovery": {
            "retry": "retry only bounded transient failures; record every retry",
            "failure": "preserve failed attempts in the next checkpoint",
            "handoff": "persist artifact, trace, verification state, and explicit next action",
        },
    }


def resolve_harness_skill(skill: str, root: Path = ROOT) -> dict[str, Any]:
    """Resolve one skill directly, without introducing a second router."""
    normalized = skill.strip().removeprefix("/")
    entrypoint = root / ".agent" / "skills" / normalized / "SKILL.md"
    if not entrypoint.is_file():
        raise ValueError(f"Unknown Beats command or skill: {skill}")
    policy = get_harness_policy(root)
    return {
        "schema_version": 1,
        "kind": "skill",
        "id": normalized,
        "triggers": [normalized],
        "inputs": ["current user request", "explicitly selected sources"],
        "entrypoint": entrypoint.relative_to(root).as_posix(),
        "context": {
            "budget_tokens": policy["context_budgets"]["skill_entrypoint_tokens"],
            "maximum_initial_sources": policy["routing"]["maximum_initial_sources"],
            "maximum_reference_hops": policy["routing"]["maximum_reference_hops"],
            "instruction": "Read this entrypoint and only its directly relevant support file; do not invoke another routing hierarchy.",
            "payload_policy": "Archive full oversized tool results with context_store.py; use compact views in active context and retain deterministic raw retrieval.",
        },
        "response": {
            "operator": "compact_operator",
            "final": "artifact",
            "verbatim_when": policy["response_profiles"]["selection"]["verbatim"],
        },
        "permissions": {
            "external_mutation": "explicit-current-turn-authorization",
            "destructive_action": "inspect-target-and-confirm-material-risk",
        },
        "quality_gate": {
            "no_functionality_regression": True,
            "raw_evidence_authoritative": True,
            "completion_criteria": ["skill contract satisfied", "required output verified"],
        },
        "checkpoint_policy": policy["checkpoint_policy"],
        "cache_policy": policy["cache_policy"],
        "runtimes": {
            "primary": policy["primary_runtimes"],
            "compatibility": policy["compatibility_runtimes"],
        },
        "outputs": {"durable": "standard repo folders", "trace": policy["telemetry"]["storage"]},
        "recovery": {
            "retry": "retry only bounded transient failures",
            "failure": "preserve failed attempts and evidence IDs",
            "handoff": "persist verification state and explicit next action",
        },
    }


def _record_resolution_usage(manifest: dict[str, Any], root: Path, wall_ms: float) -> None:
    """Append one usage ledger entry for a resolution; never break resolution on failure."""
    try:
        if manifest["kind"] == "command":
            sources = [manifest["workflow"], *manifest["context"]["candidate_required"]]
        else:
            sources = [manifest["entrypoint"]]
        loaded = 0
        total_bytes = 0
        for relative in dict.fromkeys(sources):
            path = root / relative
            if path.is_file():
                loaded += 1
                total_bytes += path.stat().st_size
        harness_telemetry.append_usage(
            manifest["id"],
            sources_loaded=loaded,
            source_bytes=total_bytes,
            wall_ms=wall_ms,
            root=root,
        )
    except Exception as exc:  # noqa: BLE001 - telemetry must never break resolution
        print(f"harness-registry: usage telemetry skipped: {exc}", file=sys.stderr)


def resolve_harness_target(target: str, root: Path = ROOT, *, record_usage: bool = True) -> dict[str, Any]:
    started = time.perf_counter()
    if resolve_command_name(target, root) is not None:
        manifest = resolve_harness_command(target, root)
    else:
        manifest = resolve_harness_skill(target, root)
    if record_usage:
        _record_resolution_usage(manifest, root, (time.perf_counter() - started) * 1000.0)
    return manifest


def audit_budgets(root: Path = ROOT) -> dict[str, Any]:
    """Audit declared context budgets against stable file-based estimates."""
    policy = get_harness_policy(root)
    budgets = policy["context_budgets"]
    violations: list[dict[str, Any]] = []
    measurements: dict[str, Any] = {"bootstrap": {}, "skills": {}, "commands": {}}

    for relative in BOOTSTRAP_PATHS:
        path = root / relative
        tokens = estimate_tokens(path.read_text(encoding="utf-8", errors="replace"))
        measurements["bootstrap"][relative] = tokens
        if tokens > budgets["runtime_bootstrap_tokens"]:
            violations.append(
                {"kind": "runtime_bootstrap", "path": relative, "tokens": tokens, "budget": budgets["runtime_bootstrap_tokens"]}
            )

    registry = compact_discovery_registry(root)
    measurements["registry_tokens"] = registry["estimated_tokens"]
    if registry["estimated_tokens"] > budgets["registry_tokens"]:
        violations.append(
            {"kind": "registry", "tokens": registry["estimated_tokens"], "budget": budgets["registry_tokens"]}
        )

    skill_manifests = sorted((root / ".agent" / "skills").glob("*/SKILL.md"))
    for path in visible_paths(skill_manifests, cwd=root):
        relative = path.relative_to(root).as_posix()
        tokens = estimate_tokens(path.read_text(encoding="utf-8", errors="replace"))
        measurements["skills"][relative] = tokens
        if tokens > budgets["skill_entrypoint_tokens"]:
            violations.append(
                {"kind": "skill_entrypoint", "path": relative, "tokens": tokens, "budget": budgets["skill_entrypoint_tokens"]}
            )

    bootstrap_floor = max(measurements["bootstrap"].values(), default=0)
    for entry in build_command_catalog(root):
        workflow = root / entry["workflow"]
        tokens = bootstrap_floor + estimate_tokens(
            workflow.read_text(encoding="utf-8", errors="replace")
        )
        measurements["commands"][entry["name"]] = tokens
        if tokens > budgets["initial_command_tokens"]:
            violations.append(
                {"kind": "initial_command", "command": entry["name"], "tokens": tokens, "budget": budgets["initial_command_tokens"]}
            )

    return {
        "ok": not violations,
        "schema_version": 1,
        "policy": {
            "name": policy["name"],
            "routing": policy["routing"],
            "context_budgets": budgets,
        },
        "measurements": measurements,
        "violations": violations,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("catalog")
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("command")
    subparsers.add_parser("doctor")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.action == "catalog":
            payload = compact_discovery_registry(root)
        elif args.action == "resolve":
            payload = resolve_harness_target(args.command, root)
        else:
            payload = audit_budgets(root)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
