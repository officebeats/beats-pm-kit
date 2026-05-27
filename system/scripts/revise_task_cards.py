#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import trello_bridge


TASKS_DIR = ROOT_DIR / "5. Trackers" / "tasks"
TASK_MASTER_PATH = ROOT_DIR / "5. Trackers" / "TASK_MASTER.md"
LANE_LABELS = {
    "triage": "Triage",
    "today": "Today",
    "next": "Next",
    "later": "Later",
    "follow_up": "Follow Up",
}


def extract_header_title(doc_text: str, task_id: str) -> str:
    match = re.search(rf"^#\s+{re.escape(task_id)}\s*(?:[—-]|:)\s+(.+)$", doc_text, flags=re.MULTILINE)
    return match.group(1).strip() if match else task_id


def split_task_cell(task_cell: str) -> tuple[str, str]:
    clean = trello_bridge.strip_markdown(task_cell.replace("->", " ")).strip()
    if " — " in clean:
        title, desc = clean.split(" — ", 1)
        return title.strip(), desc.strip()
    return clean, ""


def first_context_sentence(doc_text: str) -> str:
    section = trello_bridge.extract_section(doc_text, "Context & Background")
    if not section:
        return ""
    for chunk in re.split(r"\n\s*\n", section):
        clean = trello_bridge.strip_markdown(chunk).strip()
        if clean and not clean.startswith("|"):
            return clean
    return ""


def concise_summary_source(text: str) -> str:
    clean = trello_bridge.strip_markdown(text).strip()
    if not clean:
        return ""
    parts = re.split(r"(?<=[.!?])\s+|;\s+|:\s+", clean, maxsplit=1)
    return parts[0].strip() if parts else clean


def existing_summary_bits(doc_text: str) -> tuple[str, list[str]]:
    section = trello_bridge.extract_section(doc_text, "Card Summary")
    if not section:
        return "", []
    lines = [line.rstrip() for line in section.splitlines()]
    summary = ""
    bullets: list[str] = []
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("-"):
            bullet = trello_bridge.trim_sentence(clean.lstrip("- ").strip(), trello_bridge.SUMMARY_WORD_LIMIT)
            if bullet:
                bullets.append(bullet)
            continue
        if not summary:
            summary = trello_bridge.trim_sentence(clean, trello_bridge.SUMMARY_WORD_LIMIT)
    return summary, bullets[: trello_bridge.MAX_SUMMARY_BULLETS]


def build_summary(task_title: str, task_desc: str, doc_text: str, due: str, status: str) -> tuple[str, list[str]]:
    source = concise_summary_source(task_desc or first_context_sentence(doc_text) or task_title)
    summary = trello_bridge.trim_sentence(source, trello_bridge.SUMMARY_WORD_LIMIT)

    bullets: list[str] = []
    next_step = trello_bridge.first_section_line(doc_text, "Next Step")
    if next_step and "No explicit next step captured" not in next_step:
        bullets.append(f"Next: {trello_bridge.trim_sentence(next_step, trello_bridge.SUMMARY_WORD_LIMIT)}")
    if due:
        bullets.append(f"Due: {trello_bridge.trim_sentence(due, trello_bridge.SUMMARY_WORD_LIMIT)}")
    if status:
        status_text = status.split("—", 1)[-1].strip() if "—" in status else status.strip()
        if status_text:
            bullets.append(f"Status: {trello_bridge.trim_sentence(status_text, trello_bridge.SUMMARY_WORD_LIMIT)}")

    deduped: list[str] = []
    seen: set[str] = set()
    for bullet in bullets:
        key = bullet.lower()
        if key in seen:
            continue
        deduped.append(bullet)
        seen.add(key)
        if len(deduped) >= trello_bridge.MAX_SUMMARY_BULLETS:
            break
    return summary, deduped


def replace_task_header(doc_text: str, task_id: str, new_title: str) -> str:
    pattern = re.compile(rf"^#\s+{re.escape(task_id)}\s*(?:[—-]|:)\s+.+$", flags=re.MULTILINE)
    replacement = f"# {task_id} — {new_title}"
    if pattern.search(doc_text):
        return pattern.sub(replacement, doc_text, count=1)
    return replacement + "\n\n" + doc_text.lstrip()


def replace_lane_header(doc_text: str, lane_label: str) -> str:
    lane_line = f"> **Lane:** {lane_label}"
    patterns = [
        re.compile(r"^>\s*\*\*Lane:\*\*\s*.+$", flags=re.MULTILINE),
        re.compile(r"^>\s*\*\*Lane\*\*:\s*.+$", flags=re.MULTILINE),
        re.compile(r"^>\s*\*\*Priority:\*\*\s*.+$", flags=re.MULTILINE),
        re.compile(r"^>\s*\*\*Priority\*\*:\s*.+$", flags=re.MULTILINE),
    ]
    for pattern in patterns:
        if pattern.search(doc_text):
            return pattern.sub(lane_line, doc_text, count=1)
    return doc_text


def replace_card_summary(doc_text: str, summary_body: str) -> str:
    if "## Card Summary" in doc_text:
        return trello_bridge.replace_markdown_section(doc_text, "Card Summary", summary_body, level=2)

    block = f"## Card Summary\n\n{summary_body.strip()}\n\n---\n"
    context_pattern = re.compile(r"(?=^##\s+Context(?:\s*&\s*Background)?\b)", flags=re.MULTILINE)
    if context_pattern.search(doc_text):
        return context_pattern.sub(block, doc_text, count=1)
    return trello_bridge.replace_markdown_section(doc_text, "Card Summary", summary_body, level=2)


def normalize_urgency_labels(doc_text: str) -> str:
    replacements = {
        "**P0 / Urgent**": "**Urgent**",
        "**P1 / This Week**": "**This Week**",
        "**P2 / Track**": "**Track**",
        "**P3 / Backlog**": "**Backlog**",
        "P0 / Urgent": "Urgent",
        "P1 / This Week": "This Week",
        "P2 / Track": "Track",
        "P3 / Backlog": "Backlog",
    }
    updated = doc_text
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    return updated


def update_task_doc(task_id: str, task_cell: str, row: dict[str, str], apply: bool) -> tuple[bool, str]:
    path = TASKS_DIR / f"{task_id}.md"
    if not path.exists():
        return False, f"skip missing doc {path.name}"

    original = path.read_text(encoding="utf-8")
    title_source, desc_source = split_task_cell(task_cell)
    current_title = extract_header_title(original, task_id)
    base_title = title_source or current_title
    new_title = trello_bridge.concise_task_title(base_title, task_id=task_id) or current_title

    meta = {
        "id": task_id,
        "title": task_cell or current_title,
        "status": row.get("status", ""),
        "due": row.get("due", ""),
        "done": "✅" in row.get("status", ""),
    }
    lane_label = LANE_LABELS[trello_bridge.lane_for_task(meta)]
    summary, bullets = build_summary(base_title, desc_source, original, row.get("due", ""), row.get("status", ""))
    summary_body = summary
    if bullets:
        summary_body += "\n\n" + "\n".join(f"- {bullet}" for bullet in bullets)

    updated = original
    updated = replace_task_header(updated, task_id, new_title)
    updated = replace_lane_header(updated, lane_label)
    updated = replace_card_summary(updated, summary_body)
    updated = normalize_urgency_labels(updated)

    changed = updated != original
    if changed and apply:
        path.write_text(updated, encoding="utf-8")
    return changed, f"{task_id}: {new_title}"


def parse_task_master_rows() -> tuple[list[str], list[str]]:
    lines = TASK_MASTER_PATH.read_text(encoding="utf-8").splitlines()
    updated_lines = list(lines)
    touched_ids: list[str] = []

    for idx, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 5 or parts[0].lower() in {"id", ":---", "completed", "item"}:
            continue

        task_id = trello_bridge.extract_task_id(parts[0])
        if not task_id:
            clean = trello_bridge.strip_markdown(parts[0])
            if re.fullmatch(r"[A-Z][A-Z0-9-]+[a-z]?", clean):
                task_id = clean
        if not task_id:
            continue

        title_text, desc_text = split_task_cell(parts[1])
        new_title = trello_bridge.concise_task_title(title_text, task_id=task_id) or title_text
        summary_source = concise_summary_source(desc_text or title_text)
        new_summary = trello_bridge.trim_sentence(summary_source, trello_bridge.SUMMARY_WORD_LIMIT)
        if new_summary.lower() == new_title.lower():
            new_cell = f"**{new_title}**"
        else:
            new_cell = f"**{new_title}** — {new_summary}"

        if parts[1] != new_cell:
            parts[1] = new_cell
            updated_lines[idx] = "| " + " | ".join(parts) + " |"
            touched_ids.append(task_id)

    return lines, updated_lines


def row_lookup_from_task_master() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for line in TASK_MASTER_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 5 or parts[0].lower() in {"id", ":---", "completed", "item"}:
            continue
        task_id = trello_bridge.extract_task_id(parts[0])
        if not task_id:
            continue
        lookup[task_id] = {
            "task": parts[1],
            "owner": parts[2] if len(parts) > 2 else "",
            "due": parts[3] if len(parts) > 3 else "",
            "status": parts[4] if len(parts) > 4 else "",
        }
    return lookup


def run(apply: bool) -> int:
    _, updated_task_master_lines = parse_task_master_rows()
    task_rows = row_lookup_from_task_master()
    changed_docs: list[str] = []

    for path in sorted(TASKS_DIR.glob("*.md")):
        if path.name == "_TEMPLATE.md":
            continue
        task_id = path.stem
        row = task_rows.get(task_id, {"task": extract_header_title(path.read_text(encoding="utf-8"), task_id), "due": "", "status": ""})
        changed, note = update_task_doc(task_id, row.get("task", task_id), row, apply=apply)
        if changed:
            changed_docs.append(note)

    task_master_changed = updated_task_master_lines != TASK_MASTER_PATH.read_text(encoding="utf-8").splitlines()
    if task_master_changed and apply:
        TASK_MASTER_PATH.write_text("\n".join(updated_task_master_lines) + "\n", encoding="utf-8")

    mode = "apply" if apply else "dry-run"
    print(f"Task card revision {mode}")
    print(f"- Task docs changed: {len(changed_docs)}")
    print(f"- TASK_MASTER changed: {'yes' if task_master_changed else 'no'}")
    for note in changed_docs[:20]:
        print(f"- {note}")
    if len(changed_docs) > 20:
        print(f"- ... and {len(changed_docs) - 20} more")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Revise existing task cards to the short-title framework.")
    parser.add_argument("--apply", action="store_true", help="Write changes in place.")
    args = parser.parse_args()
    return run(apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
