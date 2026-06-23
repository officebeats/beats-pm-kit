"""
Standard I/O helpers shared by CLI scripts.

Windows shells often default to cp1252 when output is redirected, which breaks
diagnostic scripts that print symbols. Keep this tiny and dependency-free.
"""

from __future__ import annotations

import io
import sys


def force_utf8_stdio() -> None:
    """Prefer UTF-8 stdout/stderr while preserving replace-on-error behavior."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        encoding = (getattr(stream, "encoding", None) or "").lower()
        if encoding == "utf-8":
            continue
        buffer = getattr(stream, "buffer", None)
        if buffer is None:
            continue
        setattr(
            sys,
            stream_name,
            io.TextIOWrapper(buffer, encoding="utf-8", errors="replace"),
        )
