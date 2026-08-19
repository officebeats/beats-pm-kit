#!/usr/bin/env python3
"""Compatibility gate and reversible Markdown-title migration for current upgrades."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts import personal_memory
from system.utils.markdown_tables import split_cells

TARGET_VERSION = "13.2.0"
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
CORE_EVIDENCE_SOURCES = ("granola", "quill", "outlook", "teams", "slack")
ID_ONLY_RE = re.compile(r"^(?:[A-Z][A-Z0-9]+-\d{2,}|[0-9a-f]{12,})$", re.IGNORECASE)
GENERIC_STEMS = {"index", "notes", "readme", "task", "tasks", "template", "untitled", "workstream"}
MODEL_POLICY_PATH = Path(".beats/model-policy.json")
LEGACY_MODEL_PATHS = (
    Path("system/config.json"),
    Path("config/profile.yml"),
    Path("system/config/profile.yml"),
)
PREVIEW_MODEL_RE = re.compile(
    r"(?:preview|experimental|nightly|alpha|beta|\b20\d{2}[-.]\d{2})",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str
    code: str
    path: str
    message: str


@dataclass
class ProposedChange:
    path: str
    title: str
    reason: str


@dataclass
class LegacyModelPin:
    path: str
    runtime: str
    profile: str
    model: str


@dataclass
class Report:
    target_version: str = TARGET_VERSION
    scanned_markdown: int = 0
    titled_markdown: int = 0
    changes: list[ProposedChange] = field(default_factory=list)
    model_pins: list[LegacyModelPin] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    core_sources: dict[str, str] = field(default_factory=dict)
    personal_memory: dict[str, Any] = field(default_factory=dict)
    ready: bool = False

    @property
    def blockers(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "blocker"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "warning"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for relative in CONTENT_ROOTS:
        base = root / relative
        if not base.exists():
            continue
        paths.extend(
            path
            for path in base.rglob("*.md")
            if path.is_file() and path.name != ".gitkeep" and "markdown-label-backups" not in path.parts
        )
    for name in ("SETTINGS.md", "STATUS.md", "DECISION_LOG.md", "BRAIN_DUMP.md"):
        path = root / name
        if path.exists():
            paths.append(path)
    return sorted(set(paths))


def split_frontmatter(text: str) -> tuple[str, str, dict[str, str]]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return "", text, {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return "", text, {}
    raw = text[4:end]
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip().strip("\"'")
    return raw, text[end + 5 :], metadata


def h1(text: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def readable(value: str) -> bool:
    clean = re.sub(r"\s+", " ", value).strip()
    if len(clean) < 3 or ID_ONLY_RE.fullmatch(clean):
        return False
    return clean.lower() not in GENERIC_STEMS


def clean_legacy_title(value: str) -> str:
    value = re.sub(r"^[A-Z][A-Z0-9]+-\d{2,}\s*[—:|-]\s*", "", value).strip()
    return re.sub(r"\s+", " ", value)


def title_from_filename(path: Path) -> str:
    original_stem = path.stem.strip()
    if ID_ONLY_RE.fullmatch(original_stem):
        return ""
    stem = re.sub(r"^\d{4}[-_]\d{2}[-_]\d{2}[-_]?", "", original_stem)
    stem = re.sub(r"[-_]+", " ", stem).strip()
    return stem[:1].upper() + stem[1:] if stem else ""


def proposed_title(path: Path, text: str, linked_titles: set[str] | None = None) -> tuple[str, str]:
    _, body, metadata = split_frontmatter(text)
    metadata_title = clean_legacy_title(metadata.get("title", ""))
    if readable(metadata_title):
        return metadata_title, "existing frontmatter title"
    heading = clean_legacy_title(h1(body))
    if readable(heading):
        return heading, "existing H1"
    filename_title = title_from_filename(path)
    if readable(filename_title):
        return filename_title, "descriptive filename"
    candidates = {clean_legacy_title(item) for item in (linked_titles or set()) if readable(clean_legacy_title(item))}
    if len(candidates) == 1:
        return candidates.pop(), "existing human-readable link label"
    return "", ""


def _plain_label(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def linked_title_hints(root: Path, paths: list[Path]) -> dict[str, set[str]]:
    """Collect existing human labels without changing any legacy path."""
    hints: dict[str, set[str]] = {}

    def add(source: Path, target_text: str, label: str) -> None:
        if not target_text or "://" in target_text or target_text.startswith("#"):
            return
        target_text = target_text.split("#", 1)[0].replace("%20", " ")
        target = (source.parent / target_text).resolve()
        try:
            relative = target.relative_to(root.resolve()).as_posix()
        except ValueError:
            return
        title = clean_legacy_title(_plain_label(label))
        if target.suffix.lower() == ".md" and readable(title):
            hints.setdefault(relative, set()).add(title)

    for source in paths:
        text = source.read_text(encoding="utf-8", errors="replace")
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+\.md(?:#[^)]+)?)\)", text):
            add(source, target, label)
        if source == root / "5. Trackers" / "TASK_MASTER.md":
            for line in text.splitlines():
                cells = split_cells(line)
                if len(cells) < 2:
                    continue
                link = re.search(r"\]\((tasks/[^)]+\.md)\)", cells[0])
                if link:
                    emphasized = re.search(r"\*\*(.+?)\*\*", cells[1])
                    label = emphasized.group(1) if emphasized else re.split(r"\s+[—–]\s+", cells[1], maxsplit=1)[0]
                    add(source, link.group(1), label)
                    continue
                wiki = re.search(r"\[\[([^\]|]+?)(?:\\?\|([^\]]*))?\]\]", cells[0])
                if not wiki:
                    continue
                target = wiki.group(1).strip().rstrip("\\")
                alias = (wiki.group(2) or "").strip()
                if not target or not alias:
                    continue
                if target.startswith("5. Trackers/"):
                    target = target[len("5. Trackers/") :]
                if "/" not in target:
                    target = f"tasks/{target}"
                if not target.lower().endswith(".md"):
                    target = f"{target}.md"
                add(source, target, alias)
    return hints


def render_with_title(text: str, title: str) -> str:
    raw, body, metadata = split_frontmatter(text)
    escaped = title.replace("'", "''")
    if raw:
        lines = raw.splitlines()
        replaced = False
        for index, line in enumerate(lines):
            if re.match(r"^title:\s*", line, flags=re.IGNORECASE):
                lines[index] = f"title: '{escaped}'"
                replaced = True
                break
        if not replaced:
            lines.insert(0, f"title: '{escaped}'")
        frontmatter = "---\n" + "\n".join(lines) + "\n---\n\n"
    else:
        frontmatter = f"---\ntitle: '{escaped}'\n---\n\n"
    if h1(body):
        body = re.sub(r"^#\s+.+?$", f"# {title}", body, count=1, flags=re.MULTILINE)
    else:
        body = f"# {title}\n\n" + body.lstrip()
    return frontmatter + body.rstrip() + "\n"


def source_status(root: Path, source: str) -> str:
    chat_manifest = root / "3. Meetings" / "chat-transcripts" / "_manifest.json"
    if source in {"outlook", "teams", "slack"}:
        text = chat_manifest.read_text(encoding="utf-8", errors="replace").lower() if chat_manifest.exists() else ""
        return "configured" if source in text else "needs-source-window"
    if source == "quill":
        candidates = [
            root / "3. Meetings" / "transcripts" / "quill",
            Path(os.environ["APPDATA"]) / "Quill" / "quill.db" if os.environ.get("APPDATA") else None,
            Path(os.environ["LOCALAPPDATA"]) / "Quill" / "quill.db" if os.environ.get("LOCALAPPDATA") else None,
            Path.home() / "Library" / "Application Support" / "Quill" / "quill.db",
        ]
        return "available" if any(path is not None and _usable_source_path(path) for path in candidates) else "paste-or-export-required"
    if source == "granola":
        candidates = [
            root / "3. Meetings" / "transcripts" / "granola",
            Path(os.environ["APPDATA"]) / "Granola" if os.environ.get("APPDATA") else None,
            Path(os.environ["LOCALAPPDATA"]) / "Granola" if os.environ.get("LOCALAPPDATA") else None,
            Path.home() / "Library" / "Application Support" / "Granola",
        ]
        return "available" if any(path is not None and _usable_source_path(path) for path in candidates) else "paste-or-export-required"
    return "unknown"


def _usable_source_path(path: Path) -> bool:
    return path.is_file() or (path.is_dir() and any(item.is_file() for item in path.rglob("*")))


def model_runtime(model: str) -> str:
    """Map a legacy provider pin without rewriting the user's model ID."""
    normalized = model.casefold()
    if "gemini" in normalized:
        return "gemini"
    if "claude" in normalized or "anthropic" in normalized:
        return "claude"
    if "gpt" in normalized or "openai" in normalized or re.match(r"^o\d", normalized):
        return "codex"
    return "legacy"


def _legacy_model_pins(root: Path) -> tuple[list[LegacyModelPin], list[Finding]]:
    pins: list[LegacyModelPin] = []
    findings: list[Finding] = []
    for relative in LEGACY_MODEL_PATHS:
        path = root / relative
        if not path.is_file():
            continue
        try:
            if path.suffix == ".json":
                payload = json.loads(path.read_text(encoding="utf-8"))
                ai = payload.get("ai", {}) if isinstance(payload, dict) else {}
                model = ai.get("default_model") if isinstance(ai, dict) else None
            else:
                text = path.read_text(encoding="utf-8")
                match = re.search(
                    r"^\s*model:\s*['\"]?([^\s#'\"]+)", text, flags=re.MULTILINE
                )
                model = match.group(1) if match else None
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(
                Finding(
                    "blocker",
                    "invalid-legacy-model-config",
                    relative.as_posix(),
                    f"Cannot safely read legacy model configuration: {exc}",
                )
            )
            continue
        if isinstance(model, str) and model.strip() and model.strip() != "inherit":
            pins.append(
                LegacyModelPin(
                    path=relative.as_posix(),
                    runtime=model_runtime(model.strip()),
                    profile="balanced",
                    model=model.strip(),
                )
            )
    return pins, findings


def _local_model_policy(root: Path) -> tuple[dict[str, Any], Finding | None]:
    path = root / MODEL_POLICY_PATH
    if not path.exists():
        return {"schema_version": 1, "overrides": {}, "legacy_migrations": []}, None
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, Finding(
            "blocker",
            "invalid-model-policy",
            MODEL_POLICY_PATH.as_posix(),
            f"Cannot safely merge the local model policy: {exc}",
        )
    if policy.get("schema_version") != 1 or not isinstance(policy.get("overrides"), dict):
        return {}, Finding(
            "blocker",
            "invalid-model-policy",
            MODEL_POLICY_PATH.as_posix(),
            "Local model policy must use schema_version 1 with an overrides object.",
        )
    if not isinstance(policy.get("legacy_migrations", []), list):
        return {}, Finding(
            "blocker",
            "invalid-model-policy",
            MODEL_POLICY_PATH.as_posix(),
            "legacy_migrations must be a list when present.",
        )
    policy.setdefault("legacy_migrations", [])
    return policy, None


def _migration_matches(item: Any, pin: LegacyModelPin) -> bool:
    return isinstance(item, dict) and all(
        item.get(key) == value
        for key, value in {
            "source": pin.path,
            "runtime": pin.runtime,
            "profile": pin.profile,
            "model": pin.model,
        }.items()
    )


def inspect(root: Path = ROOT) -> Report:
    report = Report()
    task_ids: dict[str, str] = {}
    titles: dict[str, list[str]] = {}
    paths = markdown_files(root)
    hints = linked_title_hints(root, paths)
    for path in paths:
        report.scanned_markdown += 1
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        raw, body, metadata = split_frontmatter(text)
        current_title = clean_legacy_title(metadata.get("title", ""))
        current_h1 = clean_legacy_title(h1(body))
        relative_hints = hints.get(relative, set())
        title, reason = proposed_title(path, text, relative_hints)
        if readable(current_title) and readable(current_h1):
            report.titled_markdown += 1
        elif title:
            report.changes.append(ProposedChange(relative, title, reason))
        else:
            message = "No safe human-readable title can be derived."
            if len(relative_hints) > 1:
                message = "Multiple existing link labels disagree; choose one human-readable title before upgrading."
            report.findings.append(Finding("blocker", "ambiguous-title", relative, message))

        normalized = title.lower() if title else ""
        if normalized:
            titles.setdefault(normalized, []).append(relative)
        task_match = re.search(r"(?:^task_id:\s*|\*\*Internal ID:\*\*\s*)([A-Z][A-Z0-9]+-\d{3,}[a-z]?)", text, flags=re.MULTILINE)
        if task_match:
            task_id = task_match.group(1)
            if task_id in task_ids:
                report.findings.append(
                    Finding("blocker", "duplicate-task-id", relative, f"Task ID {task_id} also appears in {task_ids[task_id]}.")
                )
            else:
                task_ids[task_id] = relative

    for title, paths in titles.items():
        if len(paths) > 1:
            for path in paths:
                report.findings.append(Finding("warning", "duplicate-title", path, f"Title is shared by {len(paths)} files: {title}"))

    legacy_pins, model_findings = _legacy_model_pins(root)
    report.findings.extend(model_findings)
    policy, policy_finding = _local_model_policy(root)
    if policy_finding:
        report.findings.append(policy_finding)
        migrations: list[Any] = []
    else:
        migrations = policy.get("legacy_migrations", [])
    report.model_pins = [
        pin for pin in legacy_pins if not any(_migration_matches(item, pin) for item in migrations)
    ]
    for pin in report.model_pins:
        report.findings.append(
            Finding(
                "warning",
                "legacy-model-pin",
                pin.path,
                f"Preserve explicit model choice '{pin.model}' as a local {pin.runtime}/{pin.profile} override.",
            )
        )
        if PREVIEW_MODEL_RE.search(pin.model):
            report.findings.append(
                Finding(
                    "warning",
                    "preview-model-pin",
                    pin.path,
                    f"Model '{pin.model}' appears preview or dated; verify local runtime availability after migration.",
                )
            )
        if pin.runtime == "legacy":
            report.findings.append(
                Finding(
                    "warning",
                    "unsupported-model-runtime",
                    pin.path,
                    "The provider could not be identified; the choice will be preserved under a legacy runtime key and will not activate automatically.",
                )
            )
    grouped_pins: dict[tuple[str, str], set[str]] = {}
    for pin in report.model_pins:
        grouped_pins.setdefault((pin.runtime, pin.profile), set()).add(pin.model)
    for (runtime, profile), models in grouped_pins.items():
        if len(models) > 1:
            report.findings.append(
                Finding(
                    "blocker",
                    "conflicting-model-pins",
                    "local model configuration",
                    f"Conflicting {runtime}/{profile} model choices must be resolved explicitly: {', '.join(sorted(models))}",
                )
            )

    try:
        memory_config = personal_memory.load_config(root)
        report.personal_memory = {
            "config": personal_memory.CONFIG_PATH.as_posix(),
            "config_exists": personal_memory.config_path(root).exists(),
            "schema_version": memory_config["schema_version"],
            "enabled": memory_config["enabled"],
            "capture_enabled": memory_config["capture_enabled"],
            "migration": (
                "preserved"
                if personal_memory.config_path(root).exists()
                else "not-configured"
            ),
        }
    except ValueError as exc:
        report.personal_memory = {
            "config": personal_memory.CONFIG_PATH.as_posix(),
            "config_exists": personal_memory.config_path(root).exists(),
            "migration": "blocked",
        }
        report.findings.append(
            Finding(
                "blocker",
                "invalid-personal-memory-config",
                personal_memory.CONFIG_PATH.as_posix(),
                (
                    "The local personal-memory choice cannot be preserved safely: "
                    f"{exc}"
                ),
            )
        )

    task_master = root / "5. Trackers" / "TASK_MASTER.md"
    if task_master.exists():
        text = task_master.read_text(encoding="utf-8", errors="replace")
        for linked in re.findall(r"\((tasks/[^)]+\.md)\)", text):
            target = root / "5. Trackers" / linked.replace("%20", " ")
            if not target.exists():
                report.findings.append(Finding("blocker", "broken-task-link", "5. Trackers/TASK_MASTER.md", f"Missing linked task note: {linked}"))

    report.core_sources = {source: source_status(root, source) for source in CORE_EVIDENCE_SOURCES}
    for source, status in report.core_sources.items():
        if status not in {"configured", "available"}:
            report.findings.append(
                Finding("warning", "source-setup", "SETTINGS.md", f"{source.title()} is {status}; daily triangulation will need setup or pasted/exported evidence.")
            )
    report.ready = not report.blockers and not report.changes and not report.model_pins
    return report


def atomic_write(path: Path, text: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def apply_safe_changes(root: Path, report: Report) -> dict[str, Any]:
    if report.blockers:
        raise ValueError("Compatibility blockers must be resolved before title migration can run.")
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = root / ".beats" / "backups" / f"v11-upgrade-{timestamp}"
    manifest: dict[str, Any] = {"target_version": TARGET_VERSION, "created_at": timestamp, "files": []}
    prepared: list[tuple[Path, str, bool]] = []
    for change in report.changes:
        path = root / change.path
        old = path.read_text(encoding="utf-8", errors="replace")
        new = render_with_title(old, change.title)
        backup = backup_root / change.path
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
        manifest["files"].append(
            {"path": change.path, "existed": True, "before_sha256": sha256(path), "after_sha256": hashlib.sha256(new.encode("utf-8")).hexdigest()}
        )
        prepared.append((path, new, True))

    if report.model_pins:
        policy_path = root / MODEL_POLICY_PATH
        policy, policy_finding = _local_model_policy(root)
        if policy_finding:
            raise ValueError(policy_finding.message)
        existed = policy_path.exists()
        if existed:
            backup = backup_root / MODEL_POLICY_PATH
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(policy_path, backup)
        overrides = policy.setdefault("overrides", {})
        migrations = policy.setdefault("legacy_migrations", [])
        for pin in report.model_pins:
            runtime_overrides = overrides.setdefault(pin.runtime, {})
            if not isinstance(runtime_overrides, dict):
                raise ValueError(f"Invalid local override block for {pin.runtime}.")
            existing = runtime_overrides.get(pin.profile)
            if existing and existing != pin.model:
                status = "preserved-newer-choice"
            else:
                runtime_overrides[pin.profile] = pin.model
                status = "migrated"
            migrations.append(
                {
                    "source": pin.path,
                    "runtime": pin.runtime,
                    "profile": pin.profile,
                    "model": pin.model,
                    "status": status,
                }
            )
        new = json.dumps(policy, indent=2, sort_keys=True) + "\n"
        manifest["files"].append(
            {
                "path": MODEL_POLICY_PATH.as_posix(),
                "existed": existed,
                "before_sha256": sha256(policy_path) if existed else None,
                "after_sha256": hashlib.sha256(new.encode("utf-8")).hexdigest(),
            }
        )
        prepared.append((policy_path, new, existed))
    backup_root.mkdir(parents=True, exist_ok=True)
    (backup_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written: list[Path] = []
    try:
        for path, text, _existed in prepared:
            atomic_write(path, text)
            written.append(path)
    except Exception:
        for path in written:
            relative = path.relative_to(root)
            backup = backup_root / relative
            if backup.exists():
                shutil.copy2(backup, path)
            elif path.exists():
                path.unlink()
        raise
    return {"backup": backup_root.relative_to(root).as_posix(), "changed": len(prepared)}


def rollback(root: Path, backup: Path) -> dict[str, Any]:
    backup_root = backup if backup.is_absolute() else root / backup
    manifest = _load_manifest(backup_root / "manifest.json")
    restored = 0
    for item in manifest.get("files", []):
        relative = Path(str(item["path"]))
        source = backup_root / relative
        target = root / relative
        existed = bool(item.get("existed", True))
        if (existed and not source.exists()) or root.resolve() not in target.resolve().parents:
            raise ValueError(f"Invalid backup entry: {relative}")
        if existed:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.exists():
            target.unlink()
        restored += 1
    return {"backup": backup_root.relative_to(root).as_posix(), "restored": restored}


def _load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Backup manifest not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid backup manifest: {path}") from exc


def report_dict(report: Report) -> dict[str, Any]:
    data = asdict(report)
    data["blocker_count"] = len(report.blockers)
    data["warning_count"] = len(report.warnings)
    data["migration_required"] = bool(report.changes or report.model_pins)
    return data


def print_report(report: Report) -> None:
    print(f"Beats PM Kit {TARGET_VERSION} compatibility check")
    print(f"- Markdown scanned: {report.scanned_markdown}")
    print(f"- Already titled: {report.titled_markdown}")
    print(f"- Safe title updates: {len(report.changes)}")
    print(f"- Legacy model pins to preserve: {len(report.model_pins)}")
    print(f"- Blockers: {len(report.blockers)}")
    print(f"- Warnings: {len(report.warnings)}")
    for item in report.findings:
        print(f"[{item.severity}] {item.path}: {item.message}")
    if report.changes:
        print("Run with --apply only after reviewing the JSON or human-readable report.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true", help="Back up and add safe titles without renaming files")
    parser.add_argument("--rollback", type=Path, help="Restore a backup created by --apply")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.rollback:
            result = rollback(root, args.rollback)
            print(json.dumps(result, indent=2) if args.json else f"Restored {result['restored']} files from {result['backup']}.")
            return 0
        report = inspect(root)
        result: dict[str, Any] | None = None
        if args.apply:
            result = apply_safe_changes(root, report)
            report = inspect(root)
        payload = report_dict(report)
        if result:
            payload["migration"] = result
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print_report(report)
            if result:
                print(f"Changed {result['changed']} files; backup: {result['backup']}")
        if report.blockers:
            return 3
        if report.changes or report.model_pins:
            return 2
        return 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
