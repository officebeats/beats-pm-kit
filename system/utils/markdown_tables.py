"""Shared escaped-pipe-aware Markdown table helpers.

Wikilinks with aliases contain a pipe (``[[target|alias]]``). Inside a
Markdown table row a bare ``|`` splits the cell, so Obsidian (and every kit
parser) requires the escaped form ``[[target\\|alias]]`` there. Emitters
(``markdown_humanizer``) write the escaped form; parsers must therefore split
rows on UNESCAPED pipes only, and unwrap both escaped and unescaped wikilinks
when rendering cell text for humans. Every table parser in the kit should use
these helpers instead of ``line.strip("|").split("|")``.
"""

from __future__ import annotations

import re

_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")
_WIKILINK_ALIAS_RE = re.compile(r"\[\[[^\]|]*(?:\\\||\|)([^\]]+)\]\]")
_WIKILINK_PLAIN_RE = re.compile(r"\[\[([^\]]+)\]\]")


def split_cells(line: str) -> list[str]:
    """Split a Markdown table row into stripped cells.

    Returns ``[]`` when the line is not a table row or is a separator row.
    Escaped pipes (``\\|``, as used inside wikilink aliases) do not split.
    """
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    cells = [cell.strip() for cell in _UNESCAPED_PIPE_RE.split(stripped.strip("|"))]
    if any(cell.startswith(":---") or cell == "---" for cell in cells):
        return []
    return cells


def strip_wikilinks(value: str) -> str:
    """Reduce wikilinks to their human-readable text.

    ``[[target\\|alias]]`` and ``[[target|alias]]`` become ``alias``;
    ``[[target]]`` becomes ``target``. Other text is left alone.
    """
    value = _WIKILINK_ALIAS_RE.sub(r"\1", value or "")
    return _WIKILINK_PLAIN_RE.sub(r"\1", value)
