#!/usr/bin/env python3
"""Convert one trusted local file to Markdown with Microsoft MarkItDown."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MAX_INPUT_BYTES = 250 * 1024 * 1024
AUTO_INTAKE_EXTENSIONS = {
    ".csv",
    ".docx",
    ".epub",
    ".htm",
    ".html",
    ".json",
    ".msg",
    ".pdf",
    ".pptx",
    ".xls",
    ".xlsx",
    ".xml",
}
EXPLICIT_EXTENSIONS = AUTO_INTAKE_EXTENSIONS | {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".png",
    ".txt",
    ".wav",
    ".webp",
    ".zip",
}


class MarkdownIntakeError(RuntimeError):
    """Raised when a safe local conversion cannot be completed."""


def converter_command() -> list[str] | None:
    """Return a trusted local MarkItDown command without invoking a shell."""
    override = os.environ.get("BEATS_MARKITDOWN_BIN", "").strip()
    if override:
        candidate = Path(override).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]
        return None

    executable = shutil.which("markitdown")
    if executable:
        return [executable]
    if importlib.util.find_spec("markitdown") is not None:
        return [sys.executable, "-m", "markitdown"]
    return None


def default_output_path(source: Path) -> Path:
    """Return the sibling Markdown path for a source file."""
    return source.with_suffix(".md")


def validate_source(source: Path, *, automatic: bool = False) -> Path:
    """Resolve and validate one trusted local input file."""
    resolved = source.expanduser().resolve()
    if not resolved.is_file():
        raise MarkdownIntakeError(f"Input file does not exist: {source}")
    if resolved.stat().st_size > MAX_INPUT_BYTES:
        raise MarkdownIntakeError(
            f"Input exceeds the {MAX_INPUT_BYTES // (1024 * 1024)} MB safety limit: {resolved.name}"
        )

    allowed = AUTO_INTAKE_EXTENSIONS if automatic else EXPLICIT_EXTENSIONS
    if resolved.suffix.lower() not in allowed:
        mode = "automatic intake" if automatic else "conversion"
        raise MarkdownIntakeError(
            f"Unsupported file type for {mode}: {resolved.suffix or '<none>'}"
        )
    return resolved


def convert_file(
    source: Path,
    output: Path | None = None,
    *,
    automatic: bool = False,
    overwrite: bool = False,
    command: list[str] | None = None,
    timeout_seconds: int = 300,
) -> dict[str, str | int]:
    """Convert a local file atomically and return a compact result record."""
    source = validate_source(source, automatic=automatic)
    output = (output or default_output_path(source)).expanduser().resolve()
    if output.suffix.lower() != ".md":
        raise MarkdownIntakeError("Output path must end in .md")
    if source == output:
        raise MarkdownIntakeError("Input is already the requested Markdown output")
    if output.exists() and not overwrite:
        raise MarkdownIntakeError(f"Output already exists: {output}")

    command = command or converter_command()
    if not command:
        raise MarkdownIntakeError(
            "MarkItDown is unavailable. Use Python 3.10+ and install system/requirements-markitdown.txt."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)

    try:
        result = subprocess.run(
            [*command, str(source), "-o", str(temporary_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown conversion error").strip()
            raise MarkdownIntakeError(
                f"MarkItDown failed with exit code {result.returncode}: {detail}"
            )
        if not temporary_path.is_file() or temporary_path.stat().st_size == 0:
            raise MarkdownIntakeError("MarkItDown produced an empty Markdown file")
        os.replace(temporary_path, output)
    except subprocess.TimeoutExpired as exc:
        raise MarkdownIntakeError(
            f"MarkItDown exceeded the {timeout_seconds}-second timeout"
        ) from exc
    finally:
        temporary_path.unlink(missing_ok=True)

    return {
        "status": "converted",
        "source": str(source),
        "output": str(output),
        "bytes": output.stat().st_size,
        "converter": command[0],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Trusted local file to convert")
    parser.add_argument("-o", "--output", help="Markdown output path")
    parser.add_argument(
        "--automatic",
        action="store_true",
        help="Restrict conversion to the automatic intake extension allowlist",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output")
    parser.add_argument("--check", action="store_true", help="Report converter availability")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    return parser.parse_args()


def emit(payload: dict[str, object], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if payload.get("status") == "available":
        print(f"MarkItDown available: {payload['converter']}")
    elif payload.get("status") == "unavailable":
        print("MarkItDown unavailable. Install system/requirements-markitdown.txt with Python 3.10+.")
    else:
        print(f"Markdown created: {payload['output']}")


def main() -> int:
    args = parse_args()
    if args.check:
        command = converter_command()
        payload: dict[str, object] = {
            "status": "available" if command else "unavailable",
            "converter": " ".join(command) if command else None,
            "python": sys.version.split()[0],
        }
        emit(payload, as_json=args.json)
        return 0 if command else 1
    if not args.input:
        print("input is required unless --check is used", file=sys.stderr)
        return 2

    try:
        payload = convert_file(
            Path(args.input),
            Path(args.output) if args.output else None,
            automatic=args.automatic,
            overwrite=args.overwrite,
        )
    except MarkdownIntakeError as exc:
        error_payload = {"status": "error", "error": str(exc)}
        if args.json:
            print(json.dumps(error_payload, indent=2, sort_keys=True))
        else:
            print(str(exc), file=sys.stderr)
        return 2

    emit(payload, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
