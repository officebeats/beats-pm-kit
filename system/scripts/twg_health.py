#!/usr/bin/env python3
"""Report sanitized health for the optional read-only TWG integration."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


READ_ONLY_FAMILIES = ["doctor", "search", "work query", "jira get/query", "confluence get/query", "context", "goals/projects get/query"]
DISALLOWED_ACTIONS = ["create", "update", "assign", "transition", "comment", "link", "move", "archive", "delete", "upload", "permission changes"]


@dataclass
class TWGHealth:
    installed: bool
    configured: bool
    available: bool
    status: str
    version: str
    site_configured: bool
    auth_method: str
    skills_current: bool
    policy_mode: str
    fallback: str
    read_only_families: list[str]
    disallowed_actions: list[str]
    issues: list[str]


def resolve_binary(explicit: str | None = None, *, home: Path | None = None) -> Path | None:
    if explicit:
        candidate = Path(explicit).expanduser()
        return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None
    discovered = shutil.which("twg")
    if discovered:
        return Path(discovered)
    candidate = (home or Path.home()) / ".local/bin/twg"
    return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None


def unavailable(status: str = "not_installed") -> TWGHealth:
    issue = "TWG is optional and unavailable; use Rovo or local Atlassian artifacts."
    return TWGHealth(
        installed=status != "not_installed",
        configured=False,
        available=False,
        status=status,
        version="",
        site_configured=False,
        auth_method="",
        skills_current=False,
        policy_mode="read_only",
        fallback="rovo_or_local_atlassian_artifacts",
        read_only_families=READ_ONLY_FAMILIES,
        disallowed_actions=DISALLOWED_ACTIONS,
        issues=[issue],
    )


def parse_doctor(payload: dict[str, Any]) -> TWGHealth:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    build = data.get("build") if isinstance(data.get("build"), dict) else {}
    auth = data.get("auth") if isinstance(data.get("auth"), dict) else {}
    config = auth.get("config") if isinstance(auth.get("config"), dict) else {}
    resolved = auth.get("resolved") if isinstance(auth.get("resolved"), dict) else {}
    connectivity = data.get("connectivity") if isinstance(data.get("connectivity"), dict) else {}
    skills = data.get("skills") if isinstance(data.get("skills"), dict) else {}
    freshness = skills.get("freshness") if isinstance(skills.get("freshness"), list) else []
    configured = bool(config.get("loaded")) and bool(resolved.get("tokenPresent"))
    available = bool(connectivity.get("ok"))
    skills_current = bool(freshness) and all(isinstance(item, dict) and item.get("status") == "current" for item in freshness)
    status = "healthy" if available and skills_current else "available_skills_stale" if available else "connectivity_failed" if configured else "missing_auth"
    fields = config.get("fields") if isinstance(config.get("fields"), dict) else {}
    issues = [] if status == "healthy" else ["TWG is degraded; use Rovo or local Atlassian artifacts."]
    return TWGHealth(
        installed=True,
        configured=configured,
        available=available,
        status=status,
        version=str(build.get("version") or ""),
        site_configured=bool(resolved.get("site")),
        auth_method=str(fields.get("authMethod") or ""),
        skills_current=skills_current,
        policy_mode="read_only",
        fallback="none" if available else "rovo_or_local_atlassian_artifacts",
        read_only_families=READ_ONLY_FAMILIES,
        disallowed_actions=DISALLOWED_ACTIONS,
        issues=issues,
    )


def health_status(*, binary_path: str | None = None, probe: bool = True, timeout: float = 15.0, home: Path | None = None) -> TWGHealth:
    binary = resolve_binary(binary_path, home=home)
    if binary is None:
        return unavailable()
    if not probe:
        return unavailable("installed_not_probed")
    try:
        completed = subprocess.run([str(binary), "doctor", "-o", "json"], check=False, capture_output=True, text=True, timeout=timeout)
        payload = json.loads(completed.stdout)
    except subprocess.TimeoutExpired:
        return unavailable("doctor_timeout")
    except (OSError, json.JSONDecodeError):
        return unavailable("invalid_doctor_output")
    return parse_doctor(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--no-probe", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    status = health_status(binary_path=args.binary, probe=not args.no_probe, timeout=args.timeout)
    print(json.dumps(asdict(status), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
