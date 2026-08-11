#!/usr/bin/env python3
"""Keep local Markdown labels readable while preserving stable references."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
CONTENT_ROOTS = (
    "0. Incoming",
    "1. Company",
    "2. Products",
    "3. Meetings",
    "4. People",
    "5. Trackers",
    "6. Resources",
    "6. SOPs",
    "7. Partners",
    "8. Clients",
)
PRESERVED_PREFIXES = (
    "0. Incoming",
    "3. Meetings/archive",
    "3. Meetings/chat-transcripts",
    "3. Meetings/context-artifacts",
    "3. Meetings/transcripts",
    "5. Trackers/archive",
    "5. Trackers/trello",
)
SKIP_DIRS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "vendor",
}
TASKS_PREFIX = "5. Trackers/tasks/"
LABEL_MAP = Path("5. Trackers/MARKDOWN_LABELS.md")
GENERATED_HUB_PREFIX = Path("5. Trackers/graph-hubs")
HUB_INDEX = GENERATED_HUB_PREFIX / "Human-readable Hubs.md"
MANIFEST = Path(".beats/markdown-labels.json")
BACKUP_PREFIX = Path("5. Trackers/archive/markdown-label-backups")

ID_PATTERN = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+[A-Za-z]?"
ID_RE = re.compile(rf"^{ID_PATTERN}$")
ID_PREFIX_RE = re.compile(rf"^(?P<id>{ID_PATTERN})(?:\s*(?:—|–|:|-)\s*)(?P<title>.+)$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_ID_LINK_RE = re.compile(
    rf"\[(?P<id>{ID_PATTERN})\]\((?P<target>[^)\n]+\.md(?:#[^)\n]+)?)\)"
)
WIKILINK_ID_RE = re.compile(
    rf"\[\[(?P<target>[^\]|]+?)(?:\.md)?\|?(?P<alias>{ID_PATTERN})?\]\]"
)
GENERIC_TITLES = {"index", "item", "note", "notes", "task", "tasks", "untitled", "workstream"}


@dataclass(frozen=True)
class NoteLabel:
    path: str
    label: str
    agent_ref: str = ""
    preserved: bool = False
    needs_review: bool = False


@dataclass
class HumanizeResult:
    scanned: int = 0
    labeled: int = 0
    files_updated: int = 0
    task_headings_updated: int = 0
    references_updated: int = 0
    needs_review: int = 0
    applied: bool = False
    label_map: str = str(LABEL_MAP)
    manifest: str = str(MANIFEST)
    backup: Optional[str] = None
    latest_backup: Optional[str] = None
    updated_paths: list[str] = field(default_factory=list)


def split_frontmatter(text: str) -> tuple[list[str], str, dict[str, str]]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return [], text, {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return [], text, {}
    lines = text[4:end].splitlines()
    metadata: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip().strip("\"'")
    return lines, text[end + 5 :], metadata


def strip_markdown(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip(" -:|\t")


def cap_words(value: str, maximum: int = 10) -> str:
    return " ".join(strip_markdown(value).split()[:maximum]).rstrip(".?!")


def split_id(value: str) -> tuple[str, str]:
    clean = strip_markdown(value)
    match = ID_PREFIX_RE.match(clean)
    if match:
        return match.group("id"), match.group("title").strip()
    if ID_RE.fullmatch(clean):
        return clean, ""
    return "", clean


def weak_title(value: str) -> bool:
    words = re.findall(r"[A-Za-z0-9]+", value)
    return len(words) < 2 or value.lower() in GENERIC_TITLES or bool(ID_RE.fullmatch(value))


def document_title(text: str) -> str:
    _, body, metadata = split_frontmatter(text)
    if metadata.get("title"):
        return metadata["title"]
    match = H1_RE.search(body)
    return match.group(1).strip() if match else ""


def content_candidates(text: str, current_title: str) -> list[str]:
    _, body, _ = split_frontmatter(text)
    candidates = [split_id(current_title)[1]]
    for pattern in (
        r"^##\s+(?:Summary|Card Summary|Context(?:\s*&\s*Background)?)\s*$\n+([^#|>\n].+)$",
        r"^>\s*\*\*(?:Title|Task|Card):\*\*\s*(.+)$",
    ):
        candidates.extend(re.findall(pattern, body, flags=re.MULTILINE | re.IGNORECASE))
    for line in body.splitlines():
        clean = line.strip()
        if not clean or clean.startswith(("#", ">", "|", "```", "---", "<!--")):
            continue
        if re.match(r"^[-*]\s+", clean):
            continue
        candidates.append(clean)
        break
    unique: list[str] = []
    for candidate in candidates:
        clean = cap_words(split_id(candidate)[1])
        if clean and clean.lower() not in {item.lower() for item in unique}:
            unique.append(clean)
    return unique


def local_root(path: Path, root: Optional[Path] = None) -> Optional[Path]:
    path = Path(path)
    if root is not None:
        resolved = Path(root).resolve()
        try:
            path.resolve().relative_to(resolved)
            return resolved
        except ValueError:
            return None
    for index, part in enumerate(path.parts):
        if part in CONTENT_ROOTS:
            if path.is_absolute():
                return Path(*path.parts[:index]).resolve()
            return ROOT if index == 0 else Path(*path.parts[:index]).resolve()
    return None


def relative_note_path(path: Path, root: Optional[Path] = None) -> Optional[str]:
    resolved_root = local_root(path, root)
    if resolved_root is None:
        return None
    try:
        return Path(path).resolve().relative_to(resolved_root).as_posix()
    except ValueError:
        return None


def preserved(relative: str) -> bool:
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in PRESERVED_PREFIXES)


def markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in CONTENT_ROOTS:
        lane = root / name
        if not lane.exists():
            continue
        for path in lane.rglob("*"):
            relative = path.relative_to(root)
            if path.suffix.lower() not in {".md", ".markdown"} or not path.is_file():
                continue
            if any(part.startswith(".") or part in SKIP_DIRS for part in relative.parts):
                continue
            if (
                relative == LABEL_MAP
                or BACKUP_PREFIX in relative.parents
                or GENERATED_HUB_PREFIX in relative.parents
            ):
                continue
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().lower())


def task_identity(path: Path, text: str) -> tuple[str, str]:
    _, _, metadata = split_frontmatter(text)
    task_id = metadata.get("task_id", "")
    title = document_title(text)
    heading_id, clean_title = split_id(title)
    if not task_id:
        task_id = heading_id or (path.stem if ID_RE.fullmatch(path.stem) else "")
    candidates = content_candidates(text, clean_title)
    strong = [candidate for candidate in candidates if not weak_title(candidate)]
    return task_id, strong[0] if strong else (candidates[0] if candidates else "")


def render_task_identity(text: str, task_id: str, title: str) -> str:
    lines, body, _ = split_frontmatter(text)
    body = body.lstrip("\n")
    escaped = title.replace("'", "''")
    found_title = found_id = False
    for index, line in enumerate(lines):
        if re.match(r"^title:\s*", line, flags=re.IGNORECASE):
            lines[index] = f"title: '{escaped}'"
            found_title = True
        elif re.match(r"^task_id:\s*", line, flags=re.IGNORECASE):
            lines[index] = f"task_id: {task_id}"
            found_id = True
    if not found_title:
        lines.insert(0, f"title: '{escaped}'")
    if not found_id:
        lines.insert(1, f"task_id: {task_id}")
    if H1_RE.search(body):
        body = H1_RE.sub(f"# {title}", body, count=1)
    else:
        body = f"# {title}\n\n" + body.lstrip()
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body.rstrip() + "\n"


def task_labels(root: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    tasks = root / "5. Trackers" / "tasks"
    if not tasks.exists():
        return labels
    paths = [path for path in tasks.iterdir() if path.is_file() and path.suffix.lower() in {".md", ".markdown"}]
    for path in sorted(paths):
        task_id, title = task_identity(path, path.read_text(encoding="utf-8", errors="replace"))
        title = cap_words(title)
        if task_id and title and not weak_title(title):
            labels[task_id] = title
    return labels


def replace_id_links(text: str, labels: dict[str, str]) -> tuple[str, int]:
    changes = 0

    def markdown(match: re.Match[str]) -> str:
        nonlocal changes
        label = labels.get(match.group("id"))
        if not label:
            return match.group(0)
        changes += 1
        return f"[{label}]({match.group('target')})"

    def wikilink(match: re.Match[str]) -> str:
        nonlocal changes
        task_id = match.group("alias") or Path(match.group("target")).name
        label = labels.get(task_id)
        if not label:
            return match.group(0)
        changes += 1
        return f"[[{match.group('target')}|{label}]]"

    updated = MARKDOWN_ID_LINK_RE.sub(markdown, text)
    return WIKILINK_ID_RE.sub(wikilink, updated), changes


def humanize_generated_content(path: Path, content: str, *, root: Optional[Path] = None) -> str:
    """Humanize one write locally; no model call and no full workspace scan."""
    path = Path(path)
    if path.suffix.lower() not in {".md", ".markdown"}:
        return content
    relative = relative_note_path(path, root)
    resolved_root = local_root(path, root)
    if not relative or resolved_root is None or preserved(relative):
        return content
    labels = task_labels(resolved_root) if MARKDOWN_ID_LINK_RE.search(content) or WIKILINK_ID_RE.search(content) else {}
    updated, _ = replace_id_links(content, labels)
    if relative.startswith(TASKS_PREFIX):
        task_id, title = task_identity(path, updated)
        title = cap_words(title)
        if task_id and title and not weak_title(title):
            return render_task_identity(updated, task_id, title)
    return updated


def write_generated_markdown(path: Path, content: str, *, root: Optional[Path] = None) -> str:
    rendered = humanize_generated_content(path, content, root=root).rstrip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return rendered


def note_labels(root: Path) -> list[NoteLabel]:
    labels_by_id = task_labels(root)
    labels: list[NoteLabel] = []
    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        task_id, task_title = task_identity(path, text) if relative.startswith(TASKS_PREFIX) else ("", "")
        raw_title = task_title or split_id(document_title(text))[1] or path.stem.replace("-", " ").replace("_", " ")
        label = cap_words(labels_by_id.get(task_id, raw_title))
        needs_review = not label or weak_title(label)
        labels.append(NoteLabel(relative, label or "Note Needs Human Label", task_id, preserved(relative), needs_review))
    return labels


def map_link(relative: str) -> str:
    target = Path(os.path.relpath(Path(relative), LABEL_MAP.parent)).as_posix()
    return quote(target, safe="/-._~")


def note_link(origin: Path, relative: str) -> str:
    target = Path(os.path.relpath(Path(relative), origin.parent)).as_posix()
    return quote(target, safe="/-._~")


def table_value(value: str) -> str:
    return value.replace("|", "\\|")


def area_label(area: str) -> str:
    return {
        "0. Incoming": "Incoming Evidence",
        "1. Company": "Company Context",
        "2. Products": "Product Decisions",
        "3. Meetings": "Meeting Evidence",
        "4. People": "People and Stakeholder Context",
        "5. Trackers": "Tracker Reference Hubs",
        "6. Resources": "Resource Library",
        "6. SOPs": "Operating Procedures",
        "7. Partners": "Partner Context",
        "8. Clients": "Client Context",
    }.get(area, area)


def task_group_label(agent_ref: str) -> str:
    prefix = agent_ref.split("-", 1)[0]
    if prefix == "PLAN":
        return "Partner and the product Tasks"
    if prefix in {"ADM", "BOSS", "CRR", "DEID", "INTRO", "P1", "P2", "PALM", "PI"}:
        return "Planning and Administration Tasks"
    return "Other Active Tasks"


def render_hub(path: Path, title: str, description: str, labels: Sequence[NoteLabel]) -> str:
    rows = [
        f"# {title}",
        "",
        f"> Generated by `/vacuum`. {description}",
        "",
        "| Human label | Agent reference | Source note |",
        "|:---|:---|:---|",
    ]
    for item in sorted(labels, key=lambda value: (value.label.lower(), value.path.lower())):
        agent_ref = f"`{table_value(item.agent_ref)}`" if item.agent_ref else "-"
        rows.append(
            f"| [{table_value(item.label)}]({note_link(path, item.path)}) | "
            f"{agent_ref} | `{table_value(item.path)}` |"
        )
    return "\n".join(rows) + "\n"


def render_graph_hubs(labels: Sequence[NoteLabel]) -> dict[Path, str]:
    visible = [
        item
        for item in labels
        if not Path(item.path).name.startswith("_")
        and item.path != LABEL_MAP.as_posix()
        and not item.path.startswith(GENERATED_HUB_PREFIX.as_posix() + "/")
    ]
    groups: dict[str, list[NoteLabel]] = {}

    workstreams = [item for item in visible if item.path.startswith("5. Trackers/workstreams/")]
    if workstreams:
        groups["Workstream Hubs"] = workstreams

    for item in visible:
        if item.path.startswith(TASKS_PREFIX):
            groups.setdefault(task_group_label(item.agent_ref), []).append(item)

    for item in visible:
        if item.path.startswith(TASKS_PREFIX) or item.path.startswith("5. Trackers/workstreams/"):
            continue
        groups.setdefault(area_label(item.path.split("/", 1)[0]), []).append(item)

    hubs: dict[Path, str] = {}
    for title, items in sorted(groups.items()):
        path = GENERATED_HUB_PREFIX / f"{title}.md"
        hubs[path] = render_hub(path, title, "Human-readable navigation grouped by PM workstream or operating area.", items)

    index_rows = [
        "# Human-readable Hubs",
        "",
        "> Generated by `/vacuum`. Use these hubs for Obsidian graph navigation; `MARKDOWN_LABELS.md` is a reference catalog, not the graph center.",
        "",
        "## Hubs",
        "",
    ]
    for path in sorted(hubs, key=lambda value: value.stem.lower()):
        index_rows.append(f"- [{path.stem}]({note_link(HUB_INDEX, path.as_posix())})")
    hubs[HUB_INDEX] = "\n".join(index_rows) + "\n"
    return hubs


def render_map(labels: Sequence[NoteLabel]) -> str:
    hubs = render_graph_hubs(labels)
    rows = [
        "# Human-Readable Markdown Map",
        "",
        "> Generated by `/vacuum`. Human labels are ten words or fewer; stable IDs and source paths remain unchanged.",
        "> This file is a reference catalog. Obsidian graph navigation uses the human-readable hubs below.",
        "",
        "## Obsidian Graph Hubs",
        "",
        "| Hub | Source note |",
        "|:---|:---|",
    ]
    for path in sorted(hubs, key=lambda value: value.as_posix().lower()):
        rows.append(f"| [{path.stem}]({map_link(path.as_posix())}) | `{path.as_posix()}` |")
    rows.extend([
        "",
        "## Tasks",
        "",
        "| Human label | Agent reference | Note |",
        "|:---|:---|:---|",
    ])
    for item in labels:
        if item.path.startswith(TASKS_PREFIX):
            rows.append(f"| {table_value(item.label)} | `{table_value(item.agent_ref)}` | `{table_value(item.path)}` |")
    rows.extend(["", "## Full local catalog", "", "| Human label | Area | Note |", "|:---|:---|:---|"])
    for item in labels:
        rows.append(f"| {table_value(item.label)} | {table_value(item.path.split('/', 1)[0])} | `{table_value(item.path)}` |")
    return "\n".join(rows) + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == content:
        return False
    write_atomic(path, content)
    return True


def latest_backup(root: Path) -> Optional[str]:
    parent = root / BACKUP_PREFIX
    if not parent.exists():
        return None
    backups = sorted(item for item in parent.iterdir() if item.is_dir())
    return backups[-1].relative_to(root).as_posix() if backups else None


def run_humanizer(root: Path = ROOT, *, apply: bool = False) -> HumanizeResult:
    root = root.resolve()
    labels = note_labels(root)
    task_label_map = {item.agent_ref: item.label for item in labels if item.agent_ref and not item.needs_review}
    result = HumanizeResult(
        scanned=len(labels),
        labeled=len(labels),
        needs_review=sum(item.needs_review for item in labels),
        applied=apply,
        latest_backup=latest_backup(root),
    )
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S%f")
    backup_root = root / BACKUP_PREFIX / stamp
    backed_up = False

    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        if preserved(relative):
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        updated, reference_changes = replace_id_links(original, task_label_map)
        heading_changed = False
        if relative.startswith(TASKS_PREFIX):
            task_id, title = task_identity(path, updated)
            title = cap_words(task_label_map.get(task_id, title))
            if task_id and title and not weak_title(title):
                human = render_task_identity(updated, task_id, title)
                heading_changed = human != updated
                updated = human
        if updated == original:
            continue
        result.files_updated += 1
        result.references_updated += reference_changes
        result.task_headings_updated += int(heading_changed)
        result.updated_paths.append(relative)
        if apply:
            backup = backup_root / path.relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
            backed_up = True
            write_atomic(path, updated)

    if not apply:
        return result

    write_if_changed(root / LABEL_MAP, render_map(labels))
    for path, content in render_graph_hubs(labels).items():
        write_if_changed(root / path, content)
    payload_core = {
        "schema_version": 1,
        "max_words": 10,
        "scanned": len(labels),
        "preserved_prefixes": list(PRESERVED_PREFIXES),
        "notes": [asdict(item) for item in labels],
    }
    manifest_path = root / MANIFEST
    existing: dict = {}
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}
    comparable = {key: value for key, value in existing.items() if key != "generated_at"}
    if comparable != payload_core:
        payload = {
            **payload_core,
            "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        write_atomic(manifest_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if backed_up:
        result.backup = backup_root.relative_to(root).as_posix()
        result.latest_backup = result.backup
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_humanizer(args.root, apply=args.apply)
    if args.json:
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
    else:
        print(
            f"{'Applied' if args.apply else 'Previewed'} human-readable Markdown: "
            f"{result.scanned} scanned, {result.files_updated} files, "
            f"{result.references_updated} links, {result.needs_review} need review."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
