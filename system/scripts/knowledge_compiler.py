#!/usr/bin/env python3
"""Build and verify the local raw/compiled/digest/state PM knowledge layers."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = Path(".beats/knowledge/manifest.json")
COMPILED_REL = Path("6. Resources/knowledge/compiled")
DIGEST_REL = Path("6. Resources/knowledge/digest")
SCAN_ROOTS = (
    Path("0. Incoming"),
    Path("1. Company"),
    Path("2. Products"),
    Path("3. Meetings"),
    Path("4. People"),
    Path("5. Trackers"),
    Path("6. SOPs"),
    Path("6. Resources"),
    Path("7. Partners"),
    Path("8. Clients"),
)
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv"}
AUTHORIZED_WRITERS = {
    "raw": "source-capture",
    "compiled": "knowledge-compiler",
    "digest": "workflow-digest",
    "state": "task-and-status-workflows",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Source is outside the kit: {path}") from exc


def classify_layer(relative: Path) -> str:
    normalized = relative.as_posix().lower()
    if normalized.startswith(COMPILED_REL.as_posix().lower() + "/"):
        return "compiled"
    if normalized.startswith(DIGEST_REL.as_posix().lower() + "/") or "/reports/day/" in normalized or "/reports/week/" in normalized:
        return "digest"
    if relative.as_posix() in {"STATUS.md", "5. Trackers/TASK_MASTER.md", "5. Trackers/WORKSTREAMS.md"}:
        return "state"
    return "raw"


def iter_knowledge_files(root: Path) -> Iterable[Path]:
    for relative_root in SCAN_ROOTS:
        base = root / relative_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and path.name not in {".gitkeep", ".DS_Store"}:
                yield path
    for relative in [Path("STATUS.md")]:
        path = root / relative
        if path.is_file():
            yield path


def build_manifest(root: Path = ROOT, *, output: Path | None = None) -> dict[str, Any]:
    files = []
    for path in iter_knowledge_files(root):
        relative = path.relative_to(root)
        layer = classify_layer(relative)
        files.append(
            {
                "path": relative.as_posix(),
                "sha256": hash_file(path),
                "bytes": path.stat().st_size,
                "layer": layer,
                "authorized_writer": AUTHORIZED_WRITERS[layer],
                "modified_at": dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        )
    manifest = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "authority": "raw evidence remains authoritative; compiled and digest layers are navigation aids",
        "authorized_writers": AUTHORIZED_WRITERS,
        "maximum_initial_compiled_sources": 5,
        "maximum_direct_evidence_hops": 1,
        "files": files,
    }
    destination = output or root / MANIFEST_REL
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def slugify(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-") or "topic"


def compile_artifact(
    *,
    topic: str,
    body: str,
    sources: list[Path],
    layer: str = "compiled",
    root: Path = ROOT,
    output: Path | None = None,
) -> Path:
    if layer not in {"compiled", "digest"}:
        raise ValueError("Compiler may write only compiled or digest artifacts")
    if not sources:
        raise ValueError("Compiled and digest artifacts require at least one raw source")
    evidence: list[tuple[str, str]] = []
    for source in sources:
        relative = safe_relative(source, root)
        if not (root / relative).is_file():
            raise FileNotFoundError(source)
        if classify_layer(relative) != "raw":
            raise ValueError(f"Evidence must be raw, not {classify_layer(relative)}: {relative}")
        evidence.append((relative.as_posix(), hash_file(root / relative)))
    default_dir = COMPILED_REL if layer == "compiled" else DIGEST_REL
    destination = output or root / default_dir / f"{slugify(topic)}.md"
    relative_destination = safe_relative(destination, root)
    expected_dir = (root / default_dir).resolve()
    if not destination.resolve().is_relative_to(expected_dir):
        raise ValueError(f"{layer} output must stay under {default_dir}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer = AUTHORIZED_WRITERS[layer]
    lines = [
        "---",
        f"title: {topic}",
        f"topic: {topic}",
        f"layer: {layer}",
        f"writer: {writer}",
        f"generated_at: {utc_now()}",
        "authority: navigation-only",
        "---",
        "",
        body.rstrip(),
        "",
        "## Raw evidence",
        "",
    ]
    lines.extend(f"- `{path}` — `sha256:{digest}`" for path, digest in evidence)
    lines.extend(["", "> Retrieve and verify raw evidence before quotations, commitments, legal/security claims, or final citations.", ""])
    destination.write_text("\n".join(lines), encoding="utf-8")
    return root / relative_destination


def verify_artifact(path: Path, *, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    relative = path.relative_to(root)
    layer = classify_layer(relative)
    expected_writer = AUTHORIZED_WRITERS[layer]
    if f"writer: {expected_writer}" not in text:
        errors.append(f"{relative}: expected writer {expected_writer}")
    citations = re.findall(r"^- `([^`]+)` — `sha256:([0-9a-f]{64})`$", text, flags=re.MULTILINE)
    if not citations:
        errors.append(f"{relative}: missing raw evidence path and hash")
    for source_name, expected_hash in citations:
        source = root / source_name
        if not source.is_file():
            errors.append(f"{relative}: missing raw source {source_name}")
        elif classify_layer(Path(source_name)) != "raw":
            errors.append(f"{relative}: non-raw evidence {source_name}")
        elif hash_file(source) != expected_hash:
            errors.append(f"{relative}: stale source hash {source_name}")
    return errors


def verify_layers(root: Path = ROOT) -> dict[str, Any]:
    checked = 0
    errors: list[str] = []
    for relative_dir in [COMPILED_REL, DIGEST_REL]:
        base = root / relative_dir
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            checked += 1
            errors.extend(verify_artifact(path, root=root))
    return {"ok": not errors, "checked": checked, "errors": errors}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="action", required=True)
    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("--output", type=Path)
    compile_cmd = subparsers.add_parser("compile")
    compile_cmd.add_argument("--topic", required=True)
    compile_cmd.add_argument("--body-file", type=Path, required=True)
    compile_cmd.add_argument("--source", type=Path, action="append", required=True)
    compile_cmd.add_argument("--layer", choices=["compiled", "digest"], default="compiled")
    compile_cmd.add_argument("--output", type=Path)
    subparsers.add_parser("verify")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.action == "manifest":
            payload = build_manifest(root, output=args.output)
            print(json.dumps({"ok": True, "file_count": len(payload["files"]), "output": str(args.output or root / MANIFEST_REL)}, indent=2))
        elif args.action == "compile":
            path = compile_artifact(
                topic=args.topic,
                body=args.body_file.read_text(encoding="utf-8"),
                sources=args.source,
                layer=args.layer,
                root=root,
                output=args.output,
            )
            print(path)
        else:
            payload = verify_layers(root)
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0 if payload["ok"] else 1
    except (OSError, ValueError) as exc:
        print(f"knowledge-compiler: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
