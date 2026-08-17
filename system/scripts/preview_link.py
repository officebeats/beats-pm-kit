#!/usr/bin/env python3
"""Emit a clickable file:// preview URL for a markdown deliverable.

Sandboxed webviews (Orca's embedded browser) cannot read iCloud Drive
paths (`~/Library/Mobile Documents/...`), so files under iCloud are
staged as copies in `${TMPDIR}/beats-pm-preview/` and the staged copy
is linked instead. Other paths are linked directly.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
ICLOUD_MARKER = "Library/Mobile Documents"
PREVIEW_DIR = Path(tempfile.gettempdir()) / "beats-pm-preview"


def needs_staging(path: Path) -> bool:
    return ICLOUD_MARKER in str(path)


def stage_copy(source: Path) -> Path:
    try:
        relative = source.relative_to(ROOT)
    except ValueError:
        relative = Path(source.name)
    flattened = "__".join(relative.parts)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    staged = PREVIEW_DIR / flattened
    shutil.copyfile(source, staged)
    return staged


def to_url(path: Path) -> str:
    return "file://" + quote(str(path), safe="/")


def open_url(url: str) -> bool:
    """Best-effort open; never raises."""
    cli = os.environ.get("ORCA_CLI_COMMAND") or shutil.which("orca")
    commands = []
    if cli:
        commands.append([cli, "tab", "create", "--url", url, "--json"])
    if sys.platform == "darwin":
        commands.append(["open", url])
    else:
        commands.append(["xdg-open", url])
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print a webview-readable file:// preview URL for a file"
    )
    parser.add_argument("path", help="File to preview")
    parser.add_argument("--open", action="store_true", help="Open the URL (Orca CLI, else open/xdg-open)")
    parser.add_argument("--json", action="store_true", help="Print {source, staged, url, opened} JSON")
    args = parser.parse_args(argv)

    source = Path(args.path).expanduser().resolve()
    if not source.is_file():
        print(f"preview_link: file not found: {source}", file=sys.stderr)
        return 1

    staged: Path | None = None
    if needs_staging(source):
        staged = stage_copy(source)
    url = to_url(staged or source)

    opened = open_url(url) if args.open else False

    if args.json:
        print(
            json.dumps(
                {
                    "source": str(source),
                    "staged": str(staged) if staged else None,
                    "url": url,
                    "opened": opened,
                },
                indent=2,
            )
        )
    else:
        print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
