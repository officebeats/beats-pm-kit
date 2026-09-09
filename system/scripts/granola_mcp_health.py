#!/usr/bin/env python3
"""Check optional read-only Granola MCP availability for Beats PM Kit."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass

DEFAULT_GRANOLA_MCP_URL = "https://mcp.granola.ai/mcp"
READ_ONLY_TOOLS = [
    "search_meeting_notes",
    "get_meeting_transcript",
    "get_meeting_summary",
    "extract_action_items",
    "get_decisions",
]
DISALLOWED_TOOLS = [
    "create_note",
    "edit_note",
    "delete_note",
    "share_note",
    "invite_participant"
]

@dataclass
class GranolaMCPHealth:
    configured: bool
    status: str
    auth_method: str
    endpoint: str
    read_only_tools: list[str]
    disallowed_tools: list[str]
    issues: list[str]

def probe_endpoint(url: str, timeout: float = 5.0) -> tuple[bool, str]:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return True, str(response.status)
    except urllib.error.HTTPError as exc:
        # MCP servers require authentication; 401/403/405 confirms endpoint exists
        if exc.code in (401, 403, 405, 200, 301, 302):
            return True, str(exc.code)
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, exc.__class__.__name__

def health_status(url: str | None = None, probe: bool = True) -> GranolaMCPHealth:
    endpoint = url or os.environ.get("GRANOLA_MCP_URL") or DEFAULT_GRANOLA_MCP_URL
    issues: list[str] = []
    
    reachable = False
    http_status = ""
    if probe:
        reachable, http_status = probe_endpoint(endpoint)
        if not reachable:
            issues.append(f"Granola MCP endpoint is not reachable ({http_status}).")
            
    configured = True
    status = "available" if reachable else "unreachable"
    if not reachable and not probe:
        status = "configured"

    return GranolaMCPHealth(
        configured=configured,
        status=status,
        auth_method="oauth_browser",
        endpoint=endpoint,
        read_only_tools=READ_ONLY_TOOLS,
        disallowed_tools=DISALLOWED_TOOLS,
        issues=issues
    )

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Granola MCP endpoint URL")
    parser.add_argument("--no-probe", action="store_true", help="Skip HTTP probe")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    result = health_status(url=args.url, probe=not args.no_probe)
    data = asdict(result)

    indent = 2 if args.pretty else None
    print(json.dumps(data, indent=indent, sort_keys=True))
    return 0 if result.status in ("available", "configured") else 1

if __name__ == "__main__":
    raise SystemExit(main())
