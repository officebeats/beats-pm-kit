#!/usr/bin/env python3
"""Resolve and explicitly promote local model overrides for execution profiles."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts import detect_runtime
from system.utils.command_registry import (
    PROFILE_NAMES,
    build_command_catalog,
    get_escalation_signals,
    get_runtime_policy,
)


POLICY_SCHEMA_VERSION = 1
LOCAL_POLICY = Path(".beats/model-policy.json")
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+@-]{0,199}$")
PREVIEW_RE = re.compile(r"(?:preview|experimental|nightly|alpha|beta|\b20\d{2}[-.]\d{2})", re.IGNORECASE)


def policy_path(root: Path = ROOT) -> Path:
    return root / LOCAL_POLICY


def default_policy() -> dict[str, Any]:
    return {"schema_version": POLICY_SCHEMA_VERSION, "overrides": {}}


def load_policy(root: Path = ROOT) -> dict[str, Any]:
    path = policy_path(root)
    if not path.exists():
        return default_policy()
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid local model policy: {path}") from exc
    if policy.get("schema_version") != POLICY_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported local model policy schema: {policy.get('schema_version')}"
        )
    if not isinstance(policy.get("overrides"), dict):
        raise ValueError("Local model policy overrides must be an object")
    return policy


def _validate_identifier(value: str, label: str) -> str:
    if not SAFE_IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _backup(root: Path, reason: str) -> str | None:
    source = policy_path(root)
    if not source.exists():
        return None
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination = root / ".beats" / "backups" / f"model-policy-{reason}-{stamp}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination.relative_to(root).as_posix()


def _runtime_override(policy: dict[str, Any], runtime: str, profile: str) -> str | None:
    runtime_policy = policy.get("overrides", {}).get(runtime, {})
    if not isinstance(runtime_policy, dict):
        return None
    model = runtime_policy.get(profile)
    return model if isinstance(model, str) and model else None


def _command_entry(command: str, root: Path) -> dict[str, Any]:
    normalized = command.strip().split()[0].lstrip("/") if command.strip() else ""
    for entry in build_command_catalog(root):
        if normalized == entry["name"] or normalized in entry["aliases"]:
            return entry
    raise ValueError(f"Unknown command: {command}")


def resolve(
    command: str,
    *,
    signals: list[str] | tuple[str, ...] | None = None,
    root: Path = ROOT,
    runtime_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve a command to a profile and inherited or explicitly promoted model."""
    allowed_signals = set(get_escalation_signals(root))
    requested_signals = list(dict.fromkeys(signals or []))
    unknown = sorted(set(requested_signals) - allowed_signals)
    if unknown:
        raise ValueError("Unsupported escalation signal: " + ", ".join(unknown))
    entry = _command_entry(command, root)

    base_profile = str(entry["execution_profile"])
    profile = "deep" if requested_signals else base_profile
    detected = runtime_result or detect_runtime.detect_runtime(root=root)
    runtime = str(detected.get("primary", "unknown"))
    supported_profiles = detected.get("supported_profiles", [])
    profile_supported = isinstance(supported_profiles, list) and profile in supported_profiles
    warnings: list[str] = []
    downgraded = False

    if runtime == "unknown":
        downgraded = True
        warnings.append(
            "No unambiguous active runtime was detected; capabilities are denied and the runtime model remains inherited."
        )
    elif not profile_supported:
        downgraded = True
        label = profile.title()
        warnings.append(
            f"{label} support was not reported by {runtime}; using its inherited model with a visible capability downgrade."
        )

    policy = load_policy(root)
    override = _runtime_override(policy, runtime, profile) if profile_supported else None
    model = override or "inherit"
    if override and PREVIEW_RE.search(override):
        warnings.append(
            f"The explicit local model override '{override}' appears to be preview or dated; availability is not assumed."
        )
    return {
        "command": entry["name"],
        "runtime": runtime,
        "runtime_version": detected.get("primary_version"),
        "base_profile": base_profile,
        "profile": profile,
        "model": model,
        "model_source": "local-promotion" if override else "runtime",
        "escalated_by": requested_signals,
        "profile_supported": profile_supported,
        "downgraded": downgraded,
        "warnings": warnings,
    }


def status(
    *, root: Path = ROOT, runtime_result: dict[str, Any] | None = None
) -> dict[str, Any]:
    detected = runtime_result or detect_runtime.detect_runtime(root=root)
    policy = load_policy(root)
    available = set(detected.get("available_runtimes", []))
    warnings: list[str] = []
    for runtime, profiles in sorted(policy.get("overrides", {}).items()):
        if runtime not in available:
            warnings.append(
                f"Local overrides for {runtime} are preserved, but that runtime is not currently available."
            )
        if isinstance(profiles, dict):
            for profile, model in sorted(profiles.items()):
                if isinstance(model, str) and PREVIEW_RE.search(model):
                    warnings.append(
                        f"{runtime}/{profile} uses preview or dated model '{model}'; verify availability before relying on it."
                    )
    return {
        "schema_version": POLICY_SCHEMA_VERSION,
        "runtime": detected,
        "policy_path": LOCAL_POLICY.as_posix(),
        "policy_exists": policy_path(root).exists(),
        "policy": policy,
        "warnings": warnings,
    }


def _load_evaluation(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read evaluation evidence: {path}") from exc
    comparison = payload.get("comparison", {})
    if not comparison.get("recommended"):
        raise ValueError("Candidate is not recommended by the evaluation evidence")
    if not comparison.get("safety_gates_passed"):
        raise ValueError("Candidate did not pass every safety gate")
    return payload


def promote(
    runtime: str,
    profile: str,
    model: str,
    *,
    evaluation: Path,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Persist a local override only after matching recommendation evidence."""
    runtime = _validate_identifier(runtime, "runtime")
    model = _validate_identifier(model, "model ID")
    if profile not in PROFILE_NAMES:
        raise ValueError(f"Unsupported execution profile: {profile}")
    supported = set(get_runtime_policy(root).get("supported", []))
    if runtime not in supported:
        raise ValueError(f"Unsupported runtime: {runtime}")

    evaluation = evaluation.resolve()
    eval_root = (root / ".beats" / "evals").resolve()
    if eval_root != evaluation.parent and eval_root not in evaluation.parents:
        raise ValueError("Promotion evidence must stay under ignored .beats/evals storage")
    evidence = _load_evaluation(evaluation)
    candidate = evidence.get("candidate", {})
    expected = {"runtime": runtime, "profile": profile, "model": model}
    actual = {key: candidate.get(key) for key in expected}
    if actual != expected:
        raise ValueError(f"Evaluation candidate does not match promotion request: {actual}")

    policy = load_policy(root)
    overrides = policy.setdefault("overrides", {})
    runtime_overrides = overrides.setdefault(runtime, {})
    if not isinstance(runtime_overrides, dict):
        raise ValueError(f"Invalid override block for runtime: {runtime}")
    backup = _backup(root, "promote")
    runtime_overrides[profile] = model
    policy["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    policy["last_evaluation"] = str(evaluation)
    _atomic_json(policy_path(root), policy)
    return {
        "status": "promoted",
        "runtime": runtime,
        "profile": profile,
        "model": model,
        "policy": LOCAL_POLICY.as_posix(),
        "backup": backup,
    }


def reset(*, root: Path = ROOT) -> dict[str, Any]:
    path = policy_path(root)
    if not path.exists():
        return {"status": "unchanged", "policy": LOCAL_POLICY.as_posix(), "backup": None}
    backup = _backup(root, "reset")
    path.unlink()
    return {"status": "reset", "policy": LOCAL_POLICY.as_posix(), "backup": backup}


def _print_human(payload: dict[str, Any]) -> None:
    if "command" in payload:
        print(
            f"/{payload['command']}: {payload['profile']} on {payload['runtime']} "
            f"with model {payload['model']} ({payload['model_source']})"
        )
    elif payload.get("status") in {"promoted", "reset", "unchanged"}:
        print(f"Model policy: {payload['status']}")
        if payload.get("backup"):
            print(f"Backup: {payload['backup']}")
    else:
        runtime = payload["runtime"]
        print(f"Active runtime: {runtime['primary']} ({runtime['selection_status']})")
        print(f"Local policy: {'present' if payload['policy_exists'] else 'not set'}")
    for warning in payload.get("warnings", []):
        print(f"Warning: {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="action", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--json", action="store_true")

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("command")
    resolve_parser.add_argument("--signal", action="append", default=[])
    resolve_parser.add_argument("--json", action="store_true")

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("runtime")
    promote_parser.add_argument("profile", choices=PROFILE_NAMES)
    promote_parser.add_argument("model")
    promote_parser.add_argument("--evaluation", type=Path, required=True)
    promote_parser.add_argument("--json", action="store_true")

    reset_parser = subparsers.add_parser("reset")
    reset_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.action == "status":
            payload = status(root=root)
        elif args.action == "resolve":
            payload = resolve(args.command, signals=args.signal, root=root)
        elif args.action == "promote":
            payload = promote(
                args.runtime,
                args.profile,
                args.model,
                evaluation=args.evaluation.resolve(),
                root=root,
            )
        else:
            payload = reset(root=root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
