#!/usr/bin/env python3
"""Check optional agent-memory backend configuration for Beats PM Kit.

The kit treats local Markdown files as canonical. This helper only verifies
whether an external memory retrieval layer is configured well enough for an
agent runtime to try it before falling back to Obsidian MCP or repo-local rg.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from typing import Mapping


SUPPORTED_PROVIDERS = {"tenscentdb", "tencentdb"}
DEFAULT_PROVIDER = "tenscentdb"


@dataclass
class AgentMemoryHealth:
    provider: str
    configured: bool
    available: bool
    fallback: str
    mode: str
    endpoint: str
    namespace: str
    required_env: list[str]
    missing_env: list[str]
    allowed_operations: list[str]
    disallowed_operations: list[str]
    canonical_sources: list[str]
    issues: list[str]


def _first_env(env: Mapping[str, str], names: list[str]) -> str:
    for name in names:
        value = env.get(name, "").strip()
        if value:
            return value
    return ""


def health_status(
    *,
    env: Mapping[str, str] | None = None,
    provider: str | None = None,
) -> AgentMemoryHealth:
    env = env or os.environ
    provider_name = (provider or env.get("AGENT_MEMORY_PROVIDER") or DEFAULT_PROVIDER).strip().lower()
    endpoint = _first_env(env, ["AGENT_MEMORY_URL", "TENCENTDB_URL", "TENSENTDB_URL"])
    api_key = _first_env(env, ["AGENT_MEMORY_API_KEY", "TENCENTDB_API_KEY", "TENSENTDB_API_KEY"])
    namespace = _first_env(env, ["AGENT_MEMORY_NAMESPACE", "TENCENTDB_NAMESPACE", "TENSENTDB_NAMESPACE"])

    required_env = ["AGENT_MEMORY_PROVIDER", "AGENT_MEMORY_URL", "AGENT_MEMORY_API_KEY"]
    missing_env: list[str] = []
    issues: list[str] = []

    if provider_name not in SUPPORTED_PROVIDERS:
        issues.append(
            f"Unsupported agent memory provider '{provider_name}'; use tenscentdb/tencentdb or repo-local fallback."
        )

    if not endpoint:
        missing_env.append("AGENT_MEMORY_URL or TENCENTDB_URL")
    if not api_key:
        missing_env.append("AGENT_MEMORY_API_KEY or TENCENTDB_API_KEY")
    if missing_env:
        issues.append("Missing agent memory configuration; use Obsidian MCP or repo-local rg fallback.")

    configured = not missing_env and provider_name in SUPPORTED_PROVIDERS

    return AgentMemoryHealth(
        provider=provider_name,
        configured=configured,
        available=configured,
        fallback="obsidian_mcp_then_rg" if not configured else "rg_if_unavailable",
        mode="read_retrieve_only",
        endpoint=endpoint,
        namespace=namespace or "beats-pm-kit",
        required_env=required_env,
        missing_env=missing_env,
        allowed_operations=[
            "health_check",
            "semantic_search",
            "source_pointer_lookup",
            "read_retrieval_cache",
        ],
        disallowed_operations=[
            "external_memory_write",
            "external_memory_delete",
            "raw_transcript_storage",
            "secret_storage",
            "task_state_source_of_truth",
        ],
        canonical_sources=[
            "5. Trackers/TASK_MASTER.md",
            "5. Trackers/tasks/",
            "3. Meetings/chat-transcripts/_manifest.json",
            "3. Meetings/reports/",
            "4. People/",
        ],
        issues=issues,
    )


def print_human(status: AgentMemoryHealth) -> None:
    print("Agent memory health")
    print(f"- provider: {status.provider}")
    print(f"- configured: {str(status.configured).lower()}")
    print(f"- available: {str(status.available).lower()}")
    print(f"- mode: {status.mode}")
    print(f"- fallback: {status.fallback}")
    print(f"- namespace: {status.namespace}")
    if status.endpoint:
        print(f"- endpoint: {status.endpoint}")
    if status.missing_env:
        print("- missing env:")
        for name in status.missing_env:
            print(f"  - {name}")
    if status.issues:
        print("- issues:")
        for issue in status.issues:
            print(f"  - {issue}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", help="Override AGENT_MEMORY_PROVIDER for this check.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human text.")
    args = parser.parse_args()

    status = health_status(provider=args.provider)
    if args.json or args.pretty:
        print(json.dumps(asdict(status), indent=2 if args.pretty else None, sort_keys=True))
    else:
        print_human(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
