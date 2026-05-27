#!/usr/bin/env python3
"""Check optional read-only Obsidian MCP availability for Beats PM Kit."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass


DEFAULT_MCP_URL = "https://127.0.0.1:27124/mcp/"
READ_ONLY_TOOLS = [
    "vault_list",
    "vault_read",
    "vault_get_document_map",
    "active_file_get_path",
    "periodic_note_get_path",
    "search_query",
    "search_simple",
    "tag_list",
    "open_file",
]
DISALLOWED_TOOLS = [
    "vault_write",
    "vault_append",
    "vault_patch",
    "vault_delete",
    "vault_move",
    "command_execute",
]


@dataclass
class ObsidianMCPHealth:
    configured: bool
    available: bool
    status: str
    endpoint: str
    fallback: str
    read_only_tools: list[str]
    disallowed_tools: list[str]
    issues: list[str]


def probe_endpoint(url: str, api_key: str, timeout: float) -> tuple[bool, str]:
    request = urllib.request.Request(url, method="GET")
    request.add_header("Authorization", f"Bearer {api_key}")
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            if 200 <= response.status < 500:
                return True, f"http_{response.status}"
            return False, f"http_{response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            return False, f"auth_failed_http_{exc.code}"
        return True, f"http_{exc.code}"
    except Exception as exc:  # noqa: BLE001 - health checks should degrade cleanly.
        return False, exc.__class__.__name__


def health_status(
    *,
    url: str | None = None,
    api_key: str | None = None,
    probe: bool = True,
    timeout: float = 1.0,
) -> ObsidianMCPHealth:
    endpoint = url or os.environ.get("OBSIDIAN_MCP_URL") or DEFAULT_MCP_URL
    token = api_key if api_key is not None else os.environ.get("OBSIDIAN_API_KEY", "")
    issues: list[str] = []

    if not token:
        issues.append("Missing OBSIDIAN_API_KEY; Obsidian MCP will be skipped.")
        return ObsidianMCPHealth(
            configured=False,
            available=False,
            status="missing_api_key",
            endpoint=endpoint,
            fallback="rg",
            read_only_tools=READ_ONLY_TOOLS,
            disallowed_tools=DISALLOWED_TOOLS,
            issues=issues,
        )

    if not probe:
        return ObsidianMCPHealth(
            configured=True,
            available=False,
            status="configured_not_probed",
            endpoint=endpoint,
            fallback="rg_if_unavailable",
            read_only_tools=READ_ONLY_TOOLS,
            disallowed_tools=DISALLOWED_TOOLS,
            issues=[],
        )

    available, status = probe_endpoint(endpoint, token, timeout)
    if not available:
        issues.append(f"Obsidian MCP unavailable ({status}); use repo-local rg fallback.")

    return ObsidianMCPHealth(
        configured=True,
        available=available,
        status=status,
        endpoint=endpoint,
        fallback="none" if available else "rg",
        read_only_tools=READ_ONLY_TOOLS,
        disallowed_tools=DISALLOWED_TOOLS,
        issues=issues,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=None, help=f"MCP endpoint (default: {DEFAULT_MCP_URL})")
    parser.add_argument("--api-key", default=None, help="API key value. Prefer OBSIDIAN_API_KEY.")
    parser.add_argument("--timeout", type=float, default=1.0, help="Probe timeout in seconds.")
    parser.add_argument("--no-probe", action="store_true", help="Report configured profile without network probing.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    status = health_status(
        url=args.url,
        api_key=args.api_key,
        probe=not args.no_probe,
        timeout=args.timeout,
    )
    print(json.dumps(asdict(status), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
