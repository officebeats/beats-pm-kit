#!/usr/bin/env python3
"""Build and query a deterministic local context index for Beats PM Kit."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "system" / "cache" / "context-router"
INDEX_PATH = CACHE_DIR / "index.json"
WIKI_DIR = CACHE_DIR / "wiki"
KNOWLEDGE_DB_REL = Path(".beats/knowledge.db")

INDEX_VERSION = 2
MAX_INITIAL_SOURCES = 5
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv"}
MAX_SUMMARY_CHARS = 700
MAX_FILE_BYTES = 1_500_000
SCAN_ROOTS = {
    "incoming": Path("0. Incoming"),
    "company": Path("1. Company"),
    "products": Path("2. Products"),
    "tasks": Path("5. Trackers"),
    "reports": Path("3. Meetings") / "reports",
    "transcripts": Path("3. Meetings") / "transcripts",
    "chat_transcripts": Path("3. Meetings") / "chat-transcripts",
    "people": Path("4. People"),
    "partners": Path("7. Partners"),
    "clients": Path("8. Clients"),
    "sops": Path("6. SOPs"),
    "resources": Path("6. Resources"),
}
SKIP_DIRS = {
    ".git",
    ".agent",
    ".codex",
    ".claude",
    ".gemini",
    ".kilocode",
    ".context",
    ".obsidian",
    "__pycache__",
    "node_modules",
    ".next",
}
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "with",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9-]{1,}", text.lower())
    return [token for token in tokens if token not in STOP_WORDS]


def compact_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_title(path: Path, text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            match = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", text[4:end], flags=re.MULTILINE | re.IGNORECASE)
            if match:
                return compact_space(match.group(1))
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return compact_space(stripped.lstrip("# "))
    return path.stem.replace("-", " ").replace("_", " ").strip()


def knowledge_db_path(root: Path) -> Path:
    return root / KNOWLEDGE_DB_REL


def sync_knowledge_db(root: Path, index: dict[str, Any], bodies: dict[str, str]) -> Path:
    """Incrementally synchronize full Markdown bodies into a local FTS5 index."""
    db_path = knowledge_db_path(root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS document_state (path TEXT PRIMARY KEY, sha256 TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5("
            "path UNINDEXED, title, body, kind UNINDEXED, tokenize='porter unicode61')"
        )
        existing = dict(connection.execute("SELECT path, sha256 FROM document_state"))
        current_paths = {str(item["path"]) for item in index.get("files", [])}
        for removed in sorted(set(existing) - current_paths):
            connection.execute("DELETE FROM documents_fts WHERE path = ?", (removed,))
            connection.execute("DELETE FROM document_state WHERE path = ?", (removed,))
        for item in index.get("files", []):
            path = str(item["path"])
            digest = str(item["sha256"])
            if existing.get(path) == digest:
                continue
            body = bodies.get(path)
            if body is None:
                body = read_text(root / path)
            connection.execute("DELETE FROM documents_fts WHERE path = ?", (path,))
            connection.execute(
                "INSERT INTO documents_fts(path, title, body, kind) VALUES (?, ?, ?, ?)",
                (path, str(item.get("title", "")), body, str(item.get("kind", "other"))),
            )
            connection.execute(
                "INSERT INTO document_state(path, sha256) VALUES (?, ?) "
                "ON CONFLICT(path) DO UPDATE SET sha256 = excluded.sha256",
                (path, digest),
            )
        connection.commit()
    finally:
        connection.close()
    return db_path


def extract_headings(text: str, limit: int = 8) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,4}\s+\S", stripped):
            headings.append(compact_space(stripped.lstrip("# ")))
        if len(headings) >= limit:
            break
    return headings


def extract_summary(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        lines.append(stripped)
        if sum(len(item) for item in lines) >= MAX_SUMMARY_CHARS:
            break
    return compact_space(" ".join(lines))[:MAX_SUMMARY_CHARS]


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    match = re.search(
        rf"^{re.escape(key)}:\s*[\"']?(.+?)[\"']?\s*$",
        text[4:end],
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return compact_space(match.group(1)) if match else None


def context_metadata(relative_path: Path, text: str, title: str, kind: str, mtime_ns: int) -> dict[str, Any]:
    """Infer compact routing metadata without changing source authority."""
    normalized = relative_path.as_posix().lower()
    if "/compiled/" in normalized or "/knowledge/compiled/" in normalized:
        authority = "navigation"
        layer = "compiled"
    elif "/digest" in normalized or "/reports/day/" in normalized or "/reports/week/" in normalized:
        authority = "summary"
        layer = "digest"
    elif kind in {"tasks"} or relative_path.name in {"STATUS.md", "TASK_MASTER.md", "WORKSTREAMS.md"}:
        authority = "operational-state"
        layer = "state"
    else:
        authority = "raw-evidence"
        layer = "raw"
    topic = frontmatter_value(text, "topic") or title
    return {
        "authority": authority,
        "layer": layer,
        "freshness": dt.datetime.fromtimestamp(
            mtime_ns / 1_000_000_000,
            tz=dt.timezone.utc,
        ).date().isoformat(),
        "topic": topic[:160],
        "source_type": frontmatter_value(text, "source_type") or kind,
        "stakeholder": frontmatter_value(text, "stakeholder"),
        "workflow": frontmatter_value(text, "workflow"),
    }


def classify_path(relative_path: Path) -> str:
    for kind, root in SCAN_ROOTS.items():
        try:
            relative_path.relative_to(root)
            return kind
        except ValueError:
            continue
    return "other"


def iter_candidate_files(root: Path, kinds: Iterable[str] | None = None):
    selected = SCAN_ROOTS.items() if kinds is None else ((kind, SCAN_ROOTS[kind]) for kind in kinds)
    for _, relative_root in selected:
        base = root / relative_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            rel_parts = set(path.relative_to(root).parts)
            if rel_parts & SKIP_DIRS:
                continue
            if path.name in {".gitkeep", ".DS_Store"}:
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def file_stats(path: Path, root: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": path.relative_to(root).as_posix(),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }


def current_file_state(root: Path, kinds: Iterable[str] | None = None) -> dict[str, dict[str, Any]]:
    return {item["path"]: item for item in (file_stats(path, root) for path in iter_candidate_files(root, kinds))}


MTIME_CACHE_FILENAME = "mtime_cache.json"
MTIME_CACHE_SCHEMA_VERSION = 1
MTIME_CACHE_TTL_SECONDS = 300  # safety net for filesystems that don't propagate dir mtimes reliably


def _dir_tree_signature(base: Path) -> tuple[int, int]:
    """Cheap recursive fingerprint of a directory tree: (max mtime_ns, dir count).

    Stats directories only, never files, so it is far cheaper than a full
    rglob+stat walk. Creating, deleting, or renaming a file or directory
    anywhere under `base` updates its immediate parent directory's mtime, so
    this fingerprint reliably changes for any structural edit. It cannot see a
    content-only edit of an already-known file (the containing directory's
    mtime is untouched by that) — `index_is_current` covers that case with a
    targeted stat of the previously indexed files, and `MTIME_CACHE_TTL_SECONDS`
    bounds staleness for filesystems that don't propagate directory mtimes for
    nested structural changes.
    """
    try:
        max_mtime_ns = base.stat().st_mtime_ns
    except OSError:
        return (-1, -1)
    dir_count = 1
    pending = [base]
    while pending:
        current = pending.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for entry in entries:
            if entry.name in SKIP_DIRS:
                continue
            try:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                entry_mtime_ns = entry.stat(follow_symlinks=False).st_mtime_ns
            except OSError:
                continue
            dir_count += 1
            if entry_mtime_ns > max_mtime_ns:
                max_mtime_ns = entry_mtime_ns
            pending.append(Path(entry.path))
    return (max_mtime_ns, dir_count)


def _mtime_cache_path(index_path: Path) -> Path:
    return index_path.parent / MTIME_CACHE_FILENAME


def _load_mtime_cache(index_path: Path) -> dict[str, Any]:
    cache_path = _mtime_cache_path(index_path)
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if data.get("schema_version") != MTIME_CACHE_SCHEMA_VERSION:
        return {}
    return data.get("roots", {})


def _save_mtime_cache(index_path: Path, roots: dict[str, Any]) -> None:
    cache_path = _mtime_cache_path(index_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": MTIME_CACHE_SCHEMA_VERSION, "roots": roots}
    cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _mark_roots_fresh(index_path: Path, root: Path, kinds: Iterable[str] | None = None) -> None:
    """Seed/refresh the cheap directory-mtime signature after a successful full build."""
    cache = _load_mtime_cache(index_path)
    now = time.time()
    for kind, relative_root in SCAN_ROOTS.items():
        if kinds is not None and kind not in kinds:
            continue
        cache[kind] = {"signature": list(_dir_tree_signature(root / relative_root)), "checked_at": now}
    _save_mtime_cache(index_path, cache)


def _targeted_file_state(root: Path, known_paths: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Re-stat a known set of candidate files directly, skipping directory discovery."""
    state: dict[str, dict[str, Any]] = {}
    for rel_path in known_paths:
        try:
            stat = (root / rel_path).stat()
        except OSError:
            continue  # removed; its absence is caught by comparison against `indexed`
        if stat.st_size > MAX_FILE_BYTES:
            continue  # grew past the limit; comparison against `indexed` flags this as stale
        state[rel_path] = {"path": rel_path, "mtime_ns": stat.st_mtime_ns, "size": stat.st_size}
    return state


def load_index(index_path: Path = INDEX_PATH) -> dict[str, Any] | None:
    if not index_path.exists():
        return None
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def index_is_current(index: dict[str, Any] | None, root: Path, *, index_path: Path = INDEX_PATH) -> bool:
    if not index or index.get("schema_version") != INDEX_VERSION:
        return False

    indexed_by_kind: dict[str, dict[str, dict[str, Any]]] = {}
    for item in index.get("files", []):
        indexed_by_kind.setdefault(item.get("kind"), {})[item["path"]] = {
            "path": item["path"],
            "mtime_ns": item.get("mtime_ns"),
            "size": item.get("size"),
        }

    now = time.time()
    cache = _load_mtime_cache(index_path)
    signatures: dict[str, tuple[int, int]] = {}
    structurally_unchanged: set[str] = set()
    for kind, relative_root in SCAN_ROOTS.items():
        signature = _dir_tree_signature(root / relative_root)
        signatures[kind] = signature
        cached_entry = cache.get(kind)
        if (
            cached_entry is not None
            and tuple(cached_entry.get("signature", ())) == signature
            and now - cached_entry.get("checked_at", 0.0) <= MTIME_CACHE_TTL_SECONDS
        ):
            structurally_unchanged.add(kind)

    current: dict[str, dict[str, Any]] = {}
    for kind in structurally_unchanged:
        current.update(_targeted_file_state(root, indexed_by_kind.get(kind, {}).keys()))
    walked_kinds = [kind for kind in SCAN_ROOTS if kind not in structurally_unchanged]
    if walked_kinds:
        current.update(current_file_state(root, kinds=walked_kinds))

    indexed_flat = {path: item for bucket in indexed_by_kind.values() for path, item in bucket.items()}
    if indexed_flat != current:
        return False

    for kind in SCAN_ROOTS:
        cache[kind] = {"signature": list(signatures[kind]), "checked_at": now}
    _save_mtime_cache(index_path, cache)
    return True


def build_index(root: Path = ROOT, *, force: bool = False, index_path: Path = INDEX_PATH) -> dict[str, Any]:
    cached = load_index(index_path)
    if not force and index_is_current(cached, root, index_path=index_path):
        if not knowledge_db_path(root).exists():
            bodies = {path.relative_to(root).as_posix(): read_text(path) for path in iter_candidate_files(root)}
            sync_knowledge_db(root, cached, bodies)  # type: ignore[arg-type]
        return cached  # type: ignore[return-value]

    files: list[dict[str, Any]] = []
    bodies: dict[str, str] = {}
    for path in iter_candidate_files(root):
        rel_path = path.relative_to(root)
        try:
            text = read_text(path)
            stats = file_stats(path, root)
        except OSError:
            continue
        headings = extract_headings(text)
        title = extract_title(path, text)
        summary = extract_summary(text)
        search_text = " ".join([rel_path.as_posix(), title, " ".join(headings), summary])
        bodies[rel_path.as_posix()] = text
        kind = classify_path(rel_path)
        files.append(
            {
                **stats,
                "sha256": sha256_text(text),
                "kind": kind,
                "title": title,
                "headings": headings,
                "summary": summary,
                "tokens": sorted(set(tokenize(search_text))),
                **context_metadata(rel_path, text, title, kind, int(stats["mtime_ns"])),
            }
        )

    index = {
        "schema_version": INDEX_VERSION,
        "generated_at": utc_now(),
        "root": str(root),
        "scan_roots": {kind: path.as_posix() for kind, path in SCAN_ROOTS.items()},
        "files": files,
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sync_knowledge_db(root, index, bodies)
    _mark_roots_fresh(index_path, root)
    return index


def score_file(query_tokens: list[str], item: dict[str, Any]) -> tuple[int, list[str]]:
    if not query_tokens:
        return 0, []
    title = str(item.get("title", "")).lower()
    path = str(item.get("path", "")).lower()
    headings = " ".join(item.get("headings", [])).lower()
    summary = str(item.get("summary", "")).lower()
    item_tokens = set(item.get("tokens", []))

    score = 0
    reasons: list[str] = []
    for token in query_tokens:
        token_score = 0
        if token in title:
            token_score += 5
        if token in path:
            token_score += 4
        if token in headings:
            token_score += 3
        if token in item_tokens:
            token_score += 2
        if token in summary:
            token_score += 1
        if token_score:
            score += token_score
            reasons.append(token)
    return score, reasons


def missing_scopes_for(query: str, match_count: int) -> list[str]:
    lowered = query.lower()
    missing: list[str] = []
    if any(word in lowered for word in ["slack", "teams", "outlook", "calendar"]):
        missing.append("Live communication context requires an explicit named read-only source window before source-system reads.")
    if any(word in lowered for word in ["jira", "confluence"]):
        missing.append("Atlassian context is captured only from referenced local links or explicit read-only scope.")
    if match_count == 0:
        missing.append("No strong local file match found; provide a narrower topic, path, task name, or source artifact.")
    return missing


def suggested_commands_for(query: str) -> list[str]:
    lowered = query.lower()
    suggestions: list[str] = []
    if any(word in lowered for word in ["task", "todo", "owner", "due", "blocked", "follow-up"]):
        suggestions.append("/track")
    if any(word in lowered for word in ["today", "status", "priority", "daily"]):
        suggestions.append("/day")
    if any(word in lowered for word in ["meeting", "transcript", "notes"]):
        suggestions.extend(["/meet", "/transcript"])
    if any(word in lowered for word in ["prd", "spec", "document", "brief"]):
        suggestions.append("/create")
    if any(word in lowered for word in ["roadmap", "strategy", "plan"]):
        suggestions.append("/plan")
    if not suggestions:
        suggestions.append("/find")
    deduped: list[str] = []
    for suggestion in suggestions:
        if suggestion not in deduped:
            deduped.append(suggestion)
    return deduped


def _fts_expression(query_tokens: list[str], operator: str) -> str:
    return f" {operator} ".join(f'"{token}"*' for token in query_tokens)


def _matching_line(path: Path, query_tokens: list[str]) -> int:
    try:
        for number, line in enumerate(read_text(path).splitlines(), start=1):
            lowered = line.lower()
            if any(token in lowered for token in query_tokens):
                return number
    except OSError:
        return 0
    return 0


def query_knowledge_db(root: Path, query_tokens: list[str], limit: int) -> list[dict[str, Any]]:
    if not query_tokens:
        return []
    db_path = knowledge_db_path(root)
    if not db_path.exists():
        return []
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        rows: list[sqlite3.Row] = []
        for operator in ("AND", "OR"):
            rows = list(
                connection.execute(
                    "SELECT path, title, kind, "
                    "snippet(documents_fts, 2, '', '', ' … ', 24) AS excerpt, "
                    "bm25(documents_fts, 0.0, 8.0, 1.0, 0.0) AS relevance "
                    "FROM documents_fts WHERE documents_fts MATCH ? "
                    "ORDER BY relevance LIMIT ?",
                    (_fts_expression(query_tokens, operator), limit),
                )
            )
            if rows:
                break
    except sqlite3.DatabaseError:
        return []
    finally:
        connection.close()

    matches: list[dict[str, Any]] = []
    for row in rows:
        path = str(row["path"])
        title = str(row["title"])
        excerpt = compact_space(str(row["excerpt"] or ""))
        searchable = f"{title} {path} {excerpt}".lower()
        matched = [token for token in query_tokens if token in searchable]
        confidence = min(1.0, 0.35 + (0.55 * len(matched) / max(len(query_tokens), 1)) + (0.1 if any(token in title.lower() for token in query_tokens) else 0))
        matches.append(
            {
                "path": path,
                "kind": str(row["kind"]),
                "title": title,
                "score": round(-float(row["relevance"]), 5),
                "confidence": round(confidence, 3),
                "freshness": dt.datetime.fromtimestamp((root / path).stat().st_mtime, tz=dt.timezone.utc).date().isoformat(),
                "rationale": "Full-text match: " + ", ".join(matched[:6]),
                "snippet": excerpt,
                "line": _matching_line(root / path, query_tokens),
            }
        )
    return matches


def query_index(
    query: str,
    *,
    root: Path = ROOT,
    limit: int = MAX_INITIAL_SOURCES,
    index_path: Path = INDEX_PATH,
) -> dict[str, Any]:
    if not 1 <= limit <= MAX_INITIAL_SOURCES:
        raise ValueError(f"limit must be between 1 and {MAX_INITIAL_SOURCES}")
    start = time.perf_counter()
    index = build_index(root, index_path=index_path)
    query_tokens = tokenize(query)
    matches = query_knowledge_db(root, query_tokens, limit)
    index_by_path = {str(item["path"]): item for item in index.get("files", [])}
    for match in matches:
        metadata = index_by_path.get(str(match["path"]), {})
        for field in ["authority", "layer", "topic", "source_type", "stakeholder", "workflow", "sha256"]:
            match[field] = metadata.get(field)
    search_mode = "fts5"
    if not matches:
        search_mode = "metadata-fallback"
        for item in index.get("files", []):
            score, reasons = score_file(query_tokens, item)
            if score <= 0:
                continue
            max_score = max(len(query_tokens) * 10, 1)
            confidence = min(1.0, score / max_score)
            matches.append(
                {
                    "path": item["path"],
                    "kind": item["kind"],
                    "title": item["title"],
                    "score": score,
                    "confidence": round(confidence, 3),
                    "freshness": dt.datetime.fromtimestamp(
                        int(item["mtime_ns"]) / 1_000_000_000,
                        tz=dt.timezone.utc,
                    ).date().isoformat(),
                    "rationale": "Metadata match: " + ", ".join(reasons[:6]),
                    "snippet": item.get("summary", ""),
                    "line": _matching_line(root / item["path"], query_tokens),
                    "authority": item.get("authority"),
                    "layer": item.get("layer"),
                    "topic": item.get("topic"),
                    "source_type": item.get("source_type"),
                    "stakeholder": item.get("stakeholder"),
                    "workflow": item.get("workflow"),
                    "sha256": item.get("sha256"),
                }
            )
        matches.sort(key=lambda item: (-float(item["score"]), str(item["path"])))
        matches = matches[:limit]
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return {
        "schema_version": 2,
        "query": query,
        "generated_at": utc_now(),
        "index_path": index_path.relative_to(root).as_posix() if index_path.is_relative_to(root) else str(index_path),
        "elapsed_ms": elapsed_ms,
        "search_mode": search_mode,
        "matches": matches,
        "retrieval_policy": {
            "maximum_initial_sources": MAX_INITIAL_SOURCES,
            "maximum_reference_hops": 1,
            "compiled_sources_are_navigation_only": True,
            "raw_source_required_for": [
                "quotation",
                "customer-commitment",
                "legal-language",
                "security-finding",
                "final-citation",
            ],
        },
        "missing_scopes": missing_scopes_for(query, len(matches)),
        "suggested_commands": suggested_commands_for(query),
    }


def write_wiki(index: dict[str, Any], root: Path = ROOT, wiki_dir: Path = WIKI_DIR) -> Path:
    wiki_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        "# Beats PM Local Context Index",
        "",
        f"Generated: {index.get('generated_at', utc_now())}",
        "",
        "| Kind | File | Title |",
        "|:---|:---|:---|",
    ]
    for item in sorted(index.get("files", []), key=lambda entry: (entry.get("kind", ""), entry.get("path", ""))):
        rows.append(f"| {item['kind']} | `{item['path']}` | {item['title']} |")
    path = wiki_dir / "index.md"
    path.write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build/query local Beats PM context packets")
    parser.add_argument("--root", type=Path, default=ROOT, help="Kit root to index")
    parser.add_argument("--index-path", type=Path, default=None, help="Override index JSON path")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build or refresh the local context index")
    build.add_argument("--force", action="store_true", help="Rebuild even when cache appears current")
    build.add_argument("--write-wiki", action="store_true", help="Write optional Markdown wiki index")
    build.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    query = subparsers.add_parser("query", help="Return a compact source packet for a topic")
    query.add_argument("topic", nargs="+", help="Topic, task name, product area, or source hint")
    query.add_argument("--limit", type=int, default=MAX_INITIAL_SOURCES, help="Maximum matches to return (1-5)")
    query.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    find = subparsers.add_parser("find", help="Find full-text evidence in local PM history")
    find.add_argument("topic", nargs="+", help="Words or phrases from a meeting, chat, decision, task, or document")
    find.add_argument("--limit", type=int, default=MAX_INITIAL_SOURCES, help="Maximum matches to return (1-5)")
    find.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    stale = subparsers.add_parser("stale", help="Report whether the cache is stale")
    stale.add_argument("--quiet", action="store_true", help="Only use exit status")
    stale.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def emit(data: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    if isinstance(data, dict) and "matches" in data:
        print(f"Context packet for: {data['query']}")
        print(f"Elapsed: {data['elapsed_ms']} ms ({data.get('search_mode', 'local')})")
        for item in data["matches"]:
            location = f":{item['line']}" if item.get("line") else ""
            print(f"- {item['title']} — {item['path']}{location} ({item['kind']}, confidence {item['confidence']})")
            if item.get("snippet"):
                print(f"  {item['snippet']}")
        if data["missing_scopes"]:
            print("Missing scopes:")
            for scope in data["missing_scopes"]:
                print(f"- {scope}")
        print("Suggested commands: " + ", ".join(data["suggested_commands"]))
        return
    print(json.dumps(data, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    index_path = args.index_path or (root / "system" / "cache" / "context-router" / "index.json")

    if args.command == "build":
        index = build_index(root, force=args.force, index_path=index_path)
        result = {
            "ok": True,
            "index_path": str(index_path),
            "file_count": len(index.get("files", [])),
            "generated_at": index.get("generated_at"),
        }
        if args.write_wiki:
            result["wiki_path"] = str(write_wiki(index, root=root, wiki_dir=index_path.parent / "wiki"))
        emit(result, as_json=args.json)
        return 0

    if args.command in {"query", "find"}:
        topic = " ".join(args.topic)
        try:
            result = query_index(topic, root=root, limit=args.limit, index_path=index_path)
        except ValueError as exc:
            parser.error(str(exc))
        emit(result, as_json=args.json)
        return 0

    if args.command == "stale":
        index = load_index(index_path)
        stale = not index_is_current(index, root, index_path=index_path)
        if not args.quiet:
            emit({"stale": stale, "index_path": str(index_path)}, as_json=args.json)
        return 1 if stale else 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
