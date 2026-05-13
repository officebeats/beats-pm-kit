#!/usr/bin/env python3
"""
Bidirectional Trello bridge for the Beats PM kit.

The bridge keeps Trello useful as a low-latency Kanban board while preserving
the PM kit markdown files as the durable local record.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import mimetypes
import os
import plistlib
import re
import shlex
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "system" / "config" / "trello_config.json"
TEMPLATE_CONFIG_PATH = BASE_DIR / "system" / "config" / "trello_config.template.json"
TRACKERS_DIR = BASE_DIR / "5. Trackers"
TASK_MASTER_PATH = TRACKERS_DIR / "TASK_MASTER.md"
LEGACY_LEDGER_PATH = TRACKERS_DIR / ".trello_ledger.json"
TRELLO_DIR = TRACKERS_DIR / "trello"
LEDGER_PATH = TRELLO_DIR / "ledger.json"
SYNC_RUNS_DIR = TRELLO_DIR / "sync-runs"
CONFLICTS_DIR = TRELLO_DIR / "conflicts"
IMPORTANT_LINKS_DIR = TRELLO_DIR / "important-links"
NEEDS_REVIEW_DIR = TRELLO_DIR / "needs-review"
TASKS_DIR = TRACKERS_DIR / "tasks"
MEETING_NOTES_DIR = BASE_DIR / "3. Meetings" / "notes"
PEOPLE_DIR = BASE_DIR / "4. People"

DESC_BEGIN = "<!-- BEATS_PM_SYNC:BEGIN -->"
DESC_END = "<!-- BEATS_PM_SYNC:END -->"
DOC_BEGIN = "<!-- TRELLO_CARD_SYNC:BEGIN -->"
DOC_END = "<!-- TRELLO_CARD_SYNC:END -->"
HOTLIST_BEGIN = "<!-- TRELLO_HOTLIST:BEGIN -->"
HOTLIST_END = "<!-- TRELLO_HOTLIST:END -->"
MANAGED_ATTACHMENT_PREFIX = "beats-pm-snapshot-"
MANAGED_COMMENT_PREFIX = "Beats PM sync update"
MAX_WORKING_BRIEF_CHARS = 8500

WORKFLOW_LANES = {"triage", "today", "next", "later", "follow_up"}
RESOURCE_LANES = {"important_links", "meeting_notes", "people"}
EXTERNAL_FOLLOWUP_TERMS = (
    "follow up",
    "reply",
    "respond",
    "partner",
    "client",
    "customer",
    "vendor",
    "stakeholder",
    "external",
    "account",
)
LANE_STATUS = {
    "triage": "🔴 Triage",
    "today": "🟡 Today",
    "next": "🟡 Next",
    "later": "⬜ Later",
    "follow_up": "⬜ Follow Up",
}
OPERATIONAL_LABELS = {
    "P0 / Urgent": "red",
    "P1 / This Week": "orange",
    "Waiting": "yellow",
    "Needs Decision": "purple",
    "Blocked": "black",
    "External Follow-up": "sky",
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(BASE_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def now_stamp() -> str:
    return now_local().strftime("%Y-%m-%d %H:%M:%S %Z")


def today_slug() -> str:
    return now_local().strftime("%Y-%m-%d")


def parse_trello_date(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return dt.datetime.fromisoformat(value).astimezone()
    except ValueError:
        return None


def fmt_date(value: str | None) -> str:
    parsed = parse_trello_date(value)
    if not parsed:
        return ""
    return parsed.strftime("%Y-%m-%d %H:%M")


def safe_slug(value: str, fallback: str = "card") -> str:
    clean = value.lower()
    clean = re.sub(r"\([^)]*\)", "", clean)
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return clean[:80] or fallback


def strip_markdown(value: str) -> str:
    value = value.replace("~~", "")
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize(value: str) -> str:
    value = strip_markdown(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(value: str) -> set[str]:
    stop = {
        "a",
        "an",
        "and",
        "for",
        "in",
        "of",
        "on",
        "the",
        "to",
        "with",
        "work",
        "task",
        "draft",
        "prepare",
        "review",
    }
    return {part for part in normalize(value).split() if len(part) > 2 and part not in stop}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trello_state_hash(card: dict[str, Any]) -> str:
    checklists = []
    for checklist in card.get("checklists", []) or []:
        checklists.append(
            {
                "name": checklist.get("name"),
                "items": [
                    {"name": item.get("name"), "state": item.get("state")}
                    for item in checklist.get("checkItems", []) or []
                ],
            }
        )
    label_names = [
        label.get("name") or label.get("color") or label.get("id")
        for label in card.get("labels", []) or []
    ]
    state = {
        "name": card.get("name"),
        "desc": card.get("desc"),
        "idList": card.get("idList"),
        "due": card.get("due"),
        "dueComplete": card.get("dueComplete"),
        "idLabels": sorted(card.get("idLabels") or []),
        "labels": sorted(label_names),
        "checklists": checklists,
    }
    return sha256_text(json.dumps(state, sort_keys=True, ensure_ascii=True))


def ensure_dirs() -> None:
    for path in (
        TRELLO_DIR,
        SYNC_RUNS_DIR,
        CONFLICTS_DIR,
        IMPORTANT_LINKS_DIR,
        NEEDS_REVIEW_DIR,
        TASKS_DIR,
        MEETING_NOTES_DIR,
        PEOPLE_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def strip_managed_desc(desc: str) -> str:
    if DESC_BEGIN not in desc or DESC_END not in desc:
        return desc.strip()
    pattern = re.compile(
        rf"\n?\s*{re.escape(DESC_BEGIN)}.*?{re.escape(DESC_END)}\s*",
        flags=re.DOTALL,
    )
    return pattern.sub("", desc).strip()


def strip_internal_blocks(text: str) -> str:
    for begin, end in ((DESC_BEGIN, DESC_END), (DOC_BEGIN, DOC_END)):
        pattern = re.compile(
            rf"\n?\s*{re.escape(begin)}.*?{re.escape(end)}\s*",
            flags=re.DOTALL,
        )
        text = pattern.sub("\n", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"\n---\n\n\*Managed by Trello bridge.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n\*Managed by the Task Manager skill.*", "", text, flags=re.DOTALL)
    return text.strip()


def replace_block(text: str, begin: str, end: str, block: str) -> str:
    if begin in text and end in text:
        pattern = re.compile(
            rf"{re.escape(begin)}.*?{re.escape(end)}",
            flags=re.DOTALL,
        )
        return pattern.sub(block.strip(), text)

    lines = text.splitlines()
    insert_at = 0
    for idx, line in enumerate(lines):
        if idx > 0 and line.startswith("## "):
            insert_at = idx
            break
    if insert_at == 0:
        insert_at = len(lines)
    new_lines = lines[:insert_at] + ["", block.strip(), ""] + lines[insert_at:]
    return "\n".join(new_lines).rstrip() + "\n"


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(?P<body>.*?)(?=^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group("body").strip() if match else ""


def first_section_line(text: str, heading: str) -> str:
    section = extract_section(text, heading)
    for line in section.splitlines():
        clean = line.strip().lstrip("-").strip()
        if clean and not clean.startswith("|") and not clean.startswith(":"):
            return clean
    return ""


def extract_any_section(text: str, headings: list[str]) -> str:
    for heading in headings:
        section = extract_section(text, heading)
        if section:
            return section
    return ""


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


class TrelloAPI:
    def __init__(self) -> None:
        if not CONFIG_PATH.exists():
            print(f"Error: Trello configuration missing at {CONFIG_PATH}")
            print(f"Copy {TEMPLATE_CONFIG_PATH} to {CONFIG_PATH} and fill it out.")
            sys.exit(1)

        self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.api_key = self.config["api_key"]
        self.token = self.config["token"]
        self.board_id = self.config["board_id"]
        self.lane_mapping = self.config.get("lane_mapping", {})
        self.list_mapping = self.config.get("list_mapping", {})
        self.sync_completed = self.config.get("sync_completed", False)
        self.bootstrap_threshold = float(
            self.config.get("bootstrap", {}).get("auto_match_threshold", 0.74)
        )
        self.bootstrap_gap = float(
            self.config.get("bootstrap", {}).get("auto_match_gap", 0.08)
        )
        self.attach_snapshots = bool(
            self.config.get("card_docs", {}).get("attach_snapshots", True)
        )
        self.description_mode = self.config.get("card_docs", {}).get(
            "description_mode", "working_brief"
        )
        self.snapshot_policy = self.config.get("card_docs", {}).get(
            "snapshot_policy", "latest_only"
        )
        comments_config = self.config.get("comments", {})
        self.comments_enabled = bool(comments_config.get("enabled", True))
        self.comment_policy = comments_config.get("policy", "meaningful_changes")
        self.operational_labels = {
            **OPERATIONAL_LABELS,
            **self.config.get("operational_labels", {}),
        }
        self._board_long_id = self.config.get("board_long_id")
        self.reverse_lane_mapping = {v: k for k, v in self.lane_mapping.items() if v}

    def _request(
        self,
        method: str,
        path_or_url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = path_or_url
        if not url.startswith("http"):
            url = "https://api.trello.com/1" + path_or_url

        query = {"key": self.api_key, "token": self.token}
        if params:
            query.update({k: v for k, v in params.items() if v is not None})

        encoded_data = None
        headers = dict(headers or {})
        if isinstance(data, dict):
            clean_data = {k: v for k, v in data.items() if v is not None}
            if method in {"POST", "PUT"}:
                encoded_data = urllib.parse.urlencode(clean_data).encode("utf-8")
                headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
            else:
                query.update(clean_data)
        elif data is not None:
            encoded_data = data

        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urllib.parse.urlencode(query)}"
        req = urllib.request.Request(
            url,
            data=encoded_data,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            print(f"HTTP {exc.code} {method} {path_or_url}: {details}")
            return None
        except urllib.error.URLError as exc:
            print(f"Network error {method} {path_or_url}: {exc}")
            return None

    def get_lists(self) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            f"/boards/{self.board_id}/lists",
            {"fields": "name,id,pos,closed"},
        )
        return result or []

    def get_labels(self) -> list[dict[str, Any]]:
        result = self._request("GET", f"/boards/{self.board_id}/labels", {"limit": 1000})
        return result or []

    def board_long_id(self) -> str:
        if self._board_long_id:
            return self._board_long_id
        board = self._request("GET", f"/boards/{self.board_id}", {"fields": "id"})
        if isinstance(board, dict) and board.get("id"):
            self._board_long_id = board["id"]
            return self._board_long_id
        return self.board_id

    def create_label(self, name: str, color: str) -> dict[str, Any] | None:
        return self._request(
            "POST",
            "/labels",
            data={"idBoard": self.board_long_id(), "name": name, "color": color},
        )

    def get_cards(self) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            f"/boards/{self.board_id}/cards",
            {
                "fields": (
                    "name,idList,labels,idLabels,due,dueComplete,dateLastActivity,"
                    "shortUrl,desc,shortLink,pos,closed"
                ),
                "checklists": "all",
                "attachments": "true",
                "attachment_fields": "id,name,date,bytes,url",
                "limit": 1000,
            },
        )
        return result or []

    def get_card_actions(self, card_id: str, limit: int = 25) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            f"/cards/{card_id}/actions",
            {
                "filter": (
                    "commentCard,updateCard,addChecklistToCard,"
                    "updateCheckItemStateOnCard,addLabelToCard,removeLabelFromCard"
                ),
                "limit": limit,
            },
        )
        return result or []

    def update_card(self, card_id: str, **kwargs: Any) -> dict[str, Any] | None:
        return self._request("PUT", f"/cards/{card_id}", data=kwargs)

    def add_label_to_card(self, card_id: str, label_id: str) -> dict[str, Any] | None:
        return self._request("POST", f"/cards/{card_id}/idLabels", data={"value": label_id})

    def add_comment(self, card_id: str, text: str) -> dict[str, Any] | None:
        return self._request("POST", f"/cards/{card_id}/actions/comments", data={"text": text})

    def delete_attachment(self, card_id: str, attachment_id: str) -> bool:
        result = self._request("DELETE", f"/cards/{card_id}/attachments/{attachment_id}")
        return result is not None

    def attach_file(self, card_id: str, filepath: Path, name: str | None = None) -> dict[str, Any] | None:
        boundary = uuid.uuid4().hex
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        filename = name or filepath.name
        mime_type = mimetypes.guess_type(filepath.name)[0] or "text/markdown"
        file_content = filepath.read_bytes()

        fields = [
            (
                f"--{boundary}\r\n"
                'Content-Disposition: form-data; name="name"\r\n\r\n'
                f"{filename}\r\n"
            ).encode("utf-8"),
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                f"Content-Type: {mime_type}\r\n\r\n"
            ).encode("utf-8")
            + file_content
            + b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
        url = f"https://api.trello.com/1/cards/{card_id}/attachments"
        return self._request(
            "POST",
            url,
            data=b"".join(fields),
            headers=headers,
        )


def load_ledger() -> dict[str, Any]:
    if LEDGER_PATH.exists():
        ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    elif LEGACY_LEDGER_PATH.exists():
        legacy = json.loads(LEGACY_LEDGER_PATH.read_text(encoding="utf-8"))
        ledger = {"version": 2, "cards": {}, "tasks": {}, "last_run": None}
        if isinstance(legacy, dict):
            for task_id, card_id in legacy.items():
                if isinstance(task_id, str) and isinstance(card_id, str):
                    ledger["cards"][card_id] = {
                        "classification": "linked_existing",
                        "local_id": task_id,
                        "local_path": f"5. Trackers/tasks/{task_id}.md",
                    }
                    ledger["tasks"][task_id] = card_id
    else:
        ledger = {"version": 2, "cards": {}, "tasks": {}, "last_run": None}

    ledger.setdefault("version", 2)
    ledger.setdefault("cards", {})
    ledger.setdefault("tasks", {})
    return ledger


def save_ledger(ledger: dict[str, Any]) -> None:
    ensure_dirs()
    ledger["last_run"] = now_local().isoformat()
    write_text(LEDGER_PATH, json.dumps(ledger, indent=2, sort_keys=True))


def extract_task_id(cell: str) -> str:
    cell = cell.strip().replace("~~", "")
    link_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", cell)
    if link_match:
        return link_match.group(1).strip()
    clean = re.sub(r"[`*_]", "", cell).strip()
    if re.match(r"^[A-Z][A-Z0-9]*-[A-Z0-9-]+[a-z]?$", clean):
        return clean
    return ""


def extract_task_path(cell: str, task_id: str) -> Path:
    link_match = re.search(r"\[[^\]]+\]\(([^)]+)\)", cell)
    if link_match:
        target = link_match.group(1).strip()
        return (TRACKERS_DIR / target).resolve()
    return TASKS_DIR / f"{task_id}.md"


def load_task_master_tasks() -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    if not TASK_MASTER_PATH.exists():
        return tasks

    for line_no, line in enumerate(TASK_MASTER_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 5 or parts[0].lower() in {"id", ":---", "completed", "item"}:
            continue
        task_id = extract_task_id(parts[0])
        if not task_id:
            continue
        title = strip_markdown(parts[1])
        status = strip_markdown(parts[4]) if len(parts) >= 5 else ""
        candidate = {
            "id": task_id,
            "title": title,
            "owner": strip_markdown(parts[2]) if len(parts) > 2 else "",
            "due": strip_markdown(parts[3]) if len(parts) > 3 else "",
            "status": status,
            "path": extract_task_path(parts[0], task_id),
            "line": line_no,
            "done": "done" in status.lower() or "✅" in parts[4],
        }
        existing = tasks.get(task_id)
        if existing is None or (existing.get("done") and not candidate["done"]):
            tasks[task_id] = candidate
    return tasks


def card_list_name(card: dict[str, Any], lists_by_id: dict[str, str]) -> str:
    return lists_by_id.get(card.get("idList", ""), card.get("idList", ""))


def lane_for_card(api: TrelloAPI, card: dict[str, Any]) -> str:
    return api.reverse_lane_mapping.get(card.get("idList", ""), "")


def task_match_score(card: dict[str, Any], task: dict[str, Any]) -> float:
    card_name = normalize(card.get("name", ""))
    task_title = normalize(task.get("title", ""))
    card_desc = normalize(card.get("desc", ""))
    haystack = f"{card_name} {card_desc}"

    if task["id"].lower() in haystack:
        return 1.0

    name_ratio = difflib.SequenceMatcher(None, card_name, task_title).ratio()
    card_tokens = tokens(card_name)
    task_tokens = tokens(task_title)
    if not task_tokens:
        return name_ratio

    overlap = len(card_tokens & task_tokens) / max(len(card_tokens | task_tokens), 1)
    desc_overlap = len(tokens(card_desc) & task_tokens) / max(len(task_tokens), 1)

    score = max(name_ratio, 0.65 * overlap + 0.35 * name_ratio)
    score += min(desc_overlap * 0.28, 0.28)

    if "pi 56" in card_name and task["id"].startswith("PI-56"):
        score += 0.18
    if "developer portal" in haystack and "developer portal" in task_title:
        score += 0.18
    if "scorecard" in haystack and "scorecard" in task_title:
        score += 0.16

    return min(score, 1.0)


def best_task_match(
    api: TrelloAPI,
    card: dict[str, Any],
    tasks: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any] | None, float, float]:
    scores = sorted(
        ((task_match_score(card, task), task) for task in tasks.values()),
        key=lambda item: item[0],
        reverse=True,
    )
    if not scores:
        return None, 0.0, 0.0
    top_score, top_task = scores[0]
    runner_up = scores[1][0] if len(scores) > 1 else 0.0
    if top_score >= api.bootstrap_threshold and (top_score - runner_up) >= api.bootstrap_gap:
        return top_task, top_score, runner_up
    return None, top_score, runner_up


def generated_id(card: dict[str, Any]) -> str:
    return f"TR-{card.get('shortLink') or card.get('id', '')[:8]}"


def route_doc_path(
    classification: str,
    card: dict[str, Any],
    lane: str,
    task: dict[str, Any] | None = None,
) -> Path:
    if classification in {"linked_existing", "created_local"}:
        if task and task.get("path"):
            return Path(task["path"])
        return TASKS_DIR / f"{generated_id(card)}.md"
    if lane == "important_links":
        return IMPORTANT_LINKS_DIR / f"{safe_slug(card.get('name', ''), card.get('shortLink', 'card'))}.md"
    if lane == "meeting_notes":
        activity = parse_trello_date(card.get("dateLastActivity"))
        prefix = activity.strftime("%Y-%m-%d") if activity else today_slug()
        return MEETING_NOTES_DIR / f"{prefix}-{safe_slug(card.get('name', ''), card.get('shortLink', 'card'))}.md"
    if lane == "people":
        person = re.sub(r"\([^)]*\)", "", card.get("name", "")).strip()
        return PEOPLE_DIR / f"{safe_slug(person, card.get('shortLink', 'person'))}.md"
    if classification == "needs_review":
        return NEEDS_REVIEW_DIR / f"{card.get('shortLink', card.get('id', '')[:8])}-{safe_slug(card.get('name', ''), 'card')}.md"
    return TRELLO_DIR / "cards" / f"{safe_slug(card.get('name', ''), card.get('shortLink', 'card'))}.md"


def classify_card(
    api: TrelloAPI,
    card: dict[str, Any],
    tasks: dict[str, dict[str, Any]],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    lane = lane_for_card(api, card)
    entry = ledger.get("cards", {}).get(card["id"], {})
    if entry.get("classification"):
        local_id = entry.get("local_id")
        task = tasks.get(local_id) if local_id else None
        path = Path(entry.get("local_path", "")) if entry.get("local_path") else route_doc_path(entry["classification"], card, lane, task)
        if not path.is_absolute():
            path = BASE_DIR / path
        return {
            "card": card,
            "lane": lane,
            "classification": entry["classification"],
            "local_id": local_id,
            "local_path": path,
            "confidence": entry.get("confidence", 1.0),
            "runner_up": 0.0,
            "reason": "ledger",
        }

    title_id = ""
    title_match = re.search(r"\[([^\]]+)\]", card.get("name", ""))
    if title_match:
        title_id = title_match.group(1).strip()
    if title_id and title_id in tasks:
        task = tasks[title_id]
        return {
            "card": card,
            "lane": lane,
            "classification": "linked_existing",
            "local_id": title_id,
            "local_path": route_doc_path("linked_existing", card, lane, task),
            "confidence": 1.0,
            "runner_up": 0.0,
            "reason": "title_id",
        }

    if lane in RESOURCE_LANES:
        return {
            "card": card,
            "lane": lane,
            "classification": "reference_only",
            "local_id": None,
            "local_path": route_doc_path("reference_only", card, lane),
            "confidence": 1.0,
            "runner_up": 0.0,
            "reason": f"{lane}_lane",
        }

    if lane in WORKFLOW_LANES:
        task, score, runner_up = best_task_match(api, card, tasks)
        if task:
            return {
                "card": card,
                "lane": lane,
                "classification": "linked_existing",
                "local_id": task["id"],
                "local_path": route_doc_path("linked_existing", card, lane, task),
                "confidence": score,
                "runner_up": runner_up,
                "reason": "auto_match",
            }
        if score >= 0.20:
            return {
                "card": card,
                "lane": lane,
                "classification": "needs_review",
                "local_id": None,
                "local_path": route_doc_path("needs_review", card, lane),
                "confidence": score,
                "runner_up": runner_up,
                "reason": "ambiguous_match",
            }
        local_id = generated_id(card)
        return {
            "card": card,
            "lane": lane,
            "classification": "created_local",
            "local_id": local_id,
            "local_path": TASKS_DIR / f"{local_id}.md",
            "confidence": score,
            "runner_up": runner_up,
            "reason": "new_workflow_card",
        }

    return {
        "card": card,
        "lane": lane or "unknown",
        "classification": "needs_review",
        "local_id": None,
        "local_path": TRELLO_DIR / "cards" / f"{safe_slug(card.get('name', ''), card.get('shortLink', 'card'))}.md",
        "confidence": 0.0,
        "runner_up": 0.0,
        "reason": "unknown_lane",
    }


def checklist_open_items(card: dict[str, Any]) -> list[str]:
    items: list[str] = []
    for checklist in card.get("checklists", []) or []:
        for item in checklist.get("checkItems", []) or []:
            if item.get("state") != "complete":
                items.append(strip_markdown(item.get("name", "")))
    return [item for item in items if item]


def action_summary(action: dict[str, Any]) -> str:
    action_type = action.get("type", "")
    member = action.get("memberCreator", {}).get("fullName", "Trello")
    data = action.get("data", {})
    if action_type == "commentCard":
        text = data.get("text", "").strip().replace("\n", " ")
        return f"{member} commented: {text[:220]}"
    if action_type == "updateCard":
        old = data.get("old", {})
        card = data.get("card", {})
        if "idList" in old:
            before = old.get("idList", "previous list")
            after = card.get("idList", "new list")
            return f"{member} moved card from {before} to {after}"
        if "name" in old:
            return f"{member} renamed card from {old.get('name')} to {card.get('name')}"
        if "desc" in old:
            return f"{member} updated the card description"
        if "due" in old:
            return f"{member} updated the due date"
    if action_type == "updateCheckItemStateOnCard":
        item = data.get("checkItem", {}).get("name", "checklist item")
        state = data.get("checkItem", {}).get("state", "updated")
        return f"{member} marked checklist item {item} as {state}"
    if action_type == "addLabelToCard":
        label = data.get("label", {}).get("name") or data.get("label", {}).get("color", "label")
        return f"{member} added label {label}"
    if action_type == "removeLabelFromCard":
        label = data.get("label", {}).get("name") or data.get("label", {}).get("color", "label")
        return f"{member} removed label {label}"
    return f"{member} made Trello update {action_type}"


def is_managed_comment(action: dict[str, Any]) -> bool:
    if action.get("type") != "commentCard":
        return False
    text = action.get("data", {}).get("text", "") or ""
    return text.startswith(MANAGED_COMMENT_PREFIX)


def is_description_only_update(action: dict[str, Any]) -> bool:
    if action.get("type") != "updateCard":
        return False
    old = action.get("data", {}).get("old", {})
    return set(old.keys()) == {"desc"}


def latest_transpired(card: dict[str, Any], actions: list[dict[str, Any]]) -> str:
    for latest in actions:
        if is_description_only_update(latest) or is_managed_comment(latest):
            continue
        date = fmt_date(latest.get("date")) or fmt_date(card.get("dateLastActivity"))
        return f"{date} - {action_summary(latest)}"
    return "No non-description Trello activity captured yet"


def recent_activity_rows(actions: list[dict[str, Any]], limit: int = 10) -> list[str]:
    rows = []
    for action in actions:
        if is_managed_comment(action):
            continue
        rows.append(
            f"| {fmt_date(action.get('date')) or ''} | Trello | {action_summary(action).replace('|', '/')} |"
        )
        if len(rows) >= limit:
            break
    return rows


def urgency(card: dict[str, Any], lane: str) -> dict[str, Any]:
    labels = [label.get("name") or label.get("color") or "" for label in card.get("labels", [])]
    label_text = " ".join(labels).lower()
    combined = f"{card.get('name', '')} {card.get('desc', '')} {label_text}".lower()
    score = {
        "today": 50,
        "follow_up": 42,
        "triage": 30,
        "next": 22,
        "later": 6,
    }.get(lane, 12)
    drivers = [f"lane={lane or 'unknown'}"]

    due = parse_trello_date(card.get("due"))
    if due:
        delta = (due.date() - now_local().date()).days
        if delta < 0:
            score += 45
            drivers.append("overdue")
        elif delta == 0:
            score += 35
            drivers.append("due today")
        elif delta <= 2:
            score += 25
            drivers.append("due soon")
        elif delta <= 7:
            score += 15
            drivers.append("due this week")

    label_boosts = {
        "manager": 15,
        "p0": 35,
        "urgent": 30,
        "p1": 16,
        "blocked": 20,
        "waiting": 12,
        "needs decision": 18,
        "external follow-up": 12,
        "prod strategy": 8,
        "release management": 8,
        "qa": 4,
        "synapse api": 8,
    }
    for needle, boost in label_boosts.items():
        if needle in label_text:
            score += boost
            drivers.append(needle)

    if any(term in combined for term in ["blocked", "blocker", "cannot proceed"]):
        score += 18
        drivers.append("blocked text")
    if any(term in combined for term in ["decision", "decide", "approval", "approve"]):
        score += 12
        drivers.append("decision text")
    if any(term in combined for term in EXTERNAL_FOLLOWUP_TERMS):
        score += 8
        drivers.append("external follow-up")

    activity = parse_trello_date(card.get("dateLastActivity"))
    if activity:
        stale_days = (now_local() - activity).days
        if lane in {"today", "follow_up"} and stale_days >= 2:
            score += 10
            drivers.append(f"stale {stale_days}d")
        elif stale_days >= 7:
            score += 7
            drivers.append(f"stale {stale_days}d")

    if score >= 80:
        label = "P0 / Urgent"
    elif score >= 50:
        label = "P1 / This Week"
    elif score >= 35:
        label = "P2 / Track"
    else:
        label = "P3 / Backlog"
    return {"score": score, "label": label, "drivers": drivers}


def desired_label_names(card: dict[str, Any], lane: str) -> set[str]:
    desired: set[str] = set()
    urgent = urgency(card, lane)["label"]
    if urgent in {"P0 / Urgent", "P1 / This Week"}:
        desired.add(urgent)

    combined = f"{card.get('name', '')} {card.get('desc', '')}".lower()
    if lane == "follow_up" or any(term in combined for term in ["waiting", "awaiting"]):
        desired.add("Waiting")
    if any(term in combined for term in ["blocked", "blocker"]):
        desired.add("Blocked")
    if any(term in combined for term in ["decision", "decide", "approval", "approve"]):
        desired.add("Needs Decision")
    if any(term in combined for term in EXTERNAL_FOLLOWUP_TERMS):
        desired.add("External Follow-up")
    return desired


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def convert_tables_to_bullets(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    idx = 0
    while idx < len(lines):
        if (
            idx + 1 < len(lines)
            and lines[idx].strip().startswith("|")
            and is_table_separator(lines[idx + 1])
        ):
            headers = [cell.strip() for cell in lines[idx].strip().strip("|").split("|")]
            idx += 2
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[idx].strip().strip("|").split("|")]
                pairs = [
                    f"{headers[col]}: {cells[col]}"
                    for col in range(min(len(headers), len(cells)))
                    if headers[col] and cells[col]
                ]
                if pairs:
                    output.append("- " + "; ".join(pairs))
                idx += 1
            continue
        output.append(lines[idx])
        idx += 1
    return "\n".join(output)


def trello_safe_markdown(text: str, max_chars: int = 1600) -> str:
    text = strip_internal_blocks(text)
    text = convert_tables_to_bullets(text)
    safe_lines: list[str] = []
    in_code = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            safe_lines.append(line)
            continue
        if in_code:
            safe_lines.append(line)
            continue
        if line.startswith("#"):
            line = re.sub(r"^#{1,6}\s*", "### ", line)
        if re.match(r"\s*[-*]\s+\[[xX]\]", line):
            continue
        if line.strip() == "---":
            safe_lines.append("")
            continue
        safe_lines.append(line)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(safe_lines)).strip()
    if len(text) > max_chars:
        text = text[: max_chars - 24].rstrip() + "\n\n_(truncated)_"
    return text


def status_from_doc(doc_text: str) -> str:
    match = re.search(r"^>\s*\*\*Status:\*\*\s*(.+)$", doc_text, flags=re.MULTILINE)
    return strip_markdown(match.group(1)) if match else ""


def open_items_from_doc(doc_text: str) -> list[str]:
    items: list[str] = []
    for line in doc_text.splitlines():
        match = re.match(r"\s*[-*]\s+\[\s\]\s+(.+)", line)
        if match:
            item = trello_safe_markdown(match.group(1), max_chars=240)
            if item and "No open items captured yet" not in item:
                items.append(item)
    return items


def links_from_text(text: str, limit: int = 8) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)(?:\s+\"[^\"]+\")?\)", text):
        if url not in seen:
            links.append({"label": strip_markdown(label)[:80] or url, "url": url})
            seen.add(url)
    for url in re.findall(r"(?<!\()https?://[^\s)>\"]+", text):
        clean = url.rstrip(".,;")
        if clean not in seen:
            links.append({"label": clean, "url": clean})
            seen.add(clean)
    return links[:limit]


def context_from_doc(doc_text: str, fallback: str = "") -> str:
    section = extract_any_section(
        doc_text,
        ["Context & Background", "Trello Notes", "Notes", "Local Notes"],
    )
    if not section:
        section = fallback
    return trello_safe_markdown(section, max_chars=1800) or "_No context captured yet._"


def working_brief_summary(
    card: dict[str, Any],
    classification: dict[str, Any],
    actions: list[dict[str, Any]],
    doc_path: Path,
    doc_text: str,
) -> dict[str, Any]:
    lane = classification["lane"]
    urgent = urgency(card, lane)
    freeform = strip_managed_desc(card.get("desc") or "")
    open_items = open_items_from_doc(doc_text) or checklist_open_items(card)
    visible_items = open_items[:8]
    key_links = links_from_text(doc_text + "\n" + freeform)
    next_action = visible_items[0] if visible_items else "No explicit next action captured."
    return {
        "card_name": strip_markdown(card.get("name", "Untitled Trello card")),
        "last_transpired": latest_transpired(card, actions),
        "open_items": visible_items,
        "urgency": urgent["label"],
        "urgency_score": urgent["score"],
        "urgency_drivers": urgent["drivers"],
        "next_action": next_action,
        "key_links": key_links,
        "context": context_from_doc(doc_text, freeform),
        "status": status_from_doc(doc_text),
        "local_id": classification.get("local_id") or "_reference-only_",
        "local_path": rel(doc_path),
        "lane": LANE_STATUS.get(lane, lane or "Unknown"),
        "due": fmt_date(card.get("due")) or "_None_",
    }


def working_brief_digest(summary: dict[str, Any]) -> str:
    meaningful = {
        "open_items": summary.get("open_items", []),
        "urgency": summary.get("urgency"),
        "next_action": summary.get("next_action"),
        "key_links": [link["url"] for link in summary.get("key_links", [])],
        "lane": summary.get("lane"),
        "due": summary.get("due"),
        "status": summary.get("status"),
    }
    return sha256_text(json.dumps(meaningful, sort_keys=True))


def render_working_brief(summary: dict[str, Any]) -> str:
    open_items = summary.get("open_items") or []
    item_lines = "\n".join(f"- [ ] {item}" for item in open_items) if open_items else "- None captured"
    links = summary.get("key_links") or []
    link_lines = "\n".join(f"- [{link['label']}]({link['url']})" for link in links) if links else "- None captured"
    drivers = ", ".join(summary.get("urgency_drivers") or [])
    status_line = f"**Status:** {summary['status']}\n" if summary.get("status") else ""
    return textwrap.dedent(
        f"""\
        {DESC_BEGIN}
        ## Working Brief

        {status_line}**Last transpired:** {summary['last_transpired']}
        **Urgency:** {summary['urgency']} (score {summary['urgency_score']})
        **Drivers:** {drivers or "none"}
        **Lane:** {summary['lane']}
        **Due:** {summary['due']}

        **Next action:** {summary['next_action']}

        **Open items:**
        {item_lines}

        **Key links:**
        {link_lines}

        **Context:**
        {summary['context']}

        **Local ID:** `{summary['local_id']}`
        **Local doc:** `{summary['local_path']}`

        _Managed by Beats PM Kit. Human-written Trello notes above this block are preserved._
        {DESC_END}
        """
    ).strip()


def build_managed_desc(
    card: dict[str, Any],
    classification: dict[str, Any],
    actions: list[dict[str, Any]],
    doc_path: Path,
    doc_text: str = "",
    local_summary: dict[str, Any] | None = None,
) -> str:
    freeform = strip_managed_desc(card.get("desc") or "")
    if local_summary:
        summary = {
            **working_brief_summary(card, classification, actions, doc_path, doc_text),
            **local_summary,
        }
    else:
        summary = working_brief_summary(card, classification, actions, doc_path, doc_text)
    managed = render_working_brief(summary)
    desc = (freeform + "\n\n" + managed).strip() if freeform else managed
    return desc


def build_card_doc(
    card: dict[str, Any],
    classification: dict[str, Any],
    actions: list[dict[str, Any]],
    existing: str = "",
) -> str:
    lane = classification["lane"]
    local_id = classification.get("local_id") or generated_id(card)
    title = strip_markdown(card.get("name", "Untitled Trello card"))
    freeform = strip_managed_desc(card.get("desc") or "")
    open_items = checklist_open_items(card)
    urgent = urgency(card, lane)
    local_notes = extract_section(existing, "Local Notes")
    local_notes = re.split(r"\n---\n\n\*Managed by Trello bridge", local_notes)[0].strip()
    local_notes = local_notes or "_Add durable local notes here._"
    activity_rows = recent_activity_rows(actions)
    labels = ", ".join(label.get("name") or label.get("color") or "" for label in card.get("labels", [])) or "_None_"
    due = fmt_date(card.get("due")) or "_None_"
    status = LANE_STATUS.get(lane, lane or "Unknown")
    doc_kind = "Task" if classification["classification"] in {"linked_existing", "created_local"} else "Reference"

    open_item_lines = "\n".join(f"- [ ] {item}" for item in open_items) if open_items else "- [ ] No open items captured yet."
    activity_table = "\n".join(activity_rows) if activity_rows else "| | | No Trello actions captured yet |"

    return "\n".join(
        [
            f"# {local_id} - {title}",
            "",
            f"> **Kind:** {doc_kind}",
            f"> **Trello:** [{card.get('shortUrl', 'Open card')}]({card.get('shortUrl', '')})",
            f"> **Board Lane:** {status}",
            f"> **Sync Classification:** {classification['classification']}",
            f"> **Labels:** {labels}",
            f"> **Due:** {due}",
            "",
            "---",
            "",
            "## Last Transpired",
            "",
            f"- {latest_transpired(card, actions)}",
            "",
            "---",
            "",
            "## Open Items",
            "",
            open_item_lines,
            "",
            "---",
            "",
            "## Urgency",
            "",
            f"**{urgent['label']}** (score {urgent['score']})",
            "",
            f"Drivers: {', '.join(urgent['drivers'])}",
            "",
            "---",
            "",
            "## Trello Notes",
            "",
            freeform or "_No Trello body text captured yet._",
            "",
            "---",
            "",
            "## Progress Log",
            "",
            "| Date | Source | Update |",
            "|:-----|:-------|:-------|",
            activity_table,
            "",
            "---",
            "",
            "## Local Notes",
            "",
            local_notes,
            "",
            "---",
            "",
            "*Managed by Trello bridge. Trello card body and activity are synchronized into this file.*",
        ]
    )


def merge_trello_block_into_task_doc(
    card: dict[str, Any],
    classification: dict[str, Any],
    actions: list[dict[str, Any]],
    existing: str,
) -> str:
    lane = classification["lane"]
    freeform = strip_managed_desc(card.get("desc") or "")
    open_items = checklist_open_items(card)
    urgent = urgency(card, lane)
    labels = ", ".join(label.get("name") or label.get("color") or "" for label in card.get("labels", [])) or "_None_"
    due = fmt_date(card.get("due")) or "_None_"
    status = LANE_STATUS.get(lane, lane or "Unknown")
    activity_rows = recent_activity_rows(actions)
    activity_table = "\n".join(activity_rows) if activity_rows else "| | | No Trello actions captured yet |"
    open_item_lines = "\n".join(f"- [ ] {item}" for item in open_items) if open_items else "- [ ] No open items captured yet."

    block = "\n".join(
        [
            DOC_BEGIN,
            "## Trello Card Sync",
            "",
            f"> **Trello:** [{card.get('shortUrl', 'Open card')}]({card.get('shortUrl', '')})",
            f"> **Board Lane:** {status}",
            f"> **Sync Classification:** {classification['classification']}",
            f"> **Labels:** {labels}",
            f"> **Due:** {due}",
            "",
            "### Last Transpired",
            "",
            f"- {latest_transpired(card, actions)}",
            "",
            "### Open Items",
            "",
            open_item_lines,
            "",
            "### Urgency",
            "",
            f"**{urgent['label']}** (score {urgent['score']})",
            "",
            f"Drivers: {', '.join(urgent['drivers'])}",
            "",
            "### Trello Notes",
            "",
            freeform or "_No Trello body text captured yet._",
            "",
            "### Trello Activity",
            "",
            "| Date | Source | Update |",
            "|:-----|:-------|:-------|",
            activity_table,
            DOC_END,
        ]
    )
    return replace_block(existing, DOC_BEGIN, DOC_END, block)


def build_local_doc(
    card: dict[str, Any],
    classification: dict[str, Any],
    actions: list[dict[str, Any]],
    existing: str = "",
) -> str:
    if (
        classification["classification"] == "linked_existing"
        and existing
        and classification["local_path"].is_relative_to(TASKS_DIR)
    ):
        return merge_trello_block_into_task_doc(card, classification, actions, existing)
    return build_card_doc(card, classification, actions, existing)


def extract_local_summary(doc_text: str) -> dict[str, Any]:
    open_items = []
    for line in extract_section(doc_text, "Open Items").splitlines():
        match = re.match(r"- \[[ xX]\]\s*(.+)", line.strip())
        if match:
            open_items.append(match.group(1).strip())
    urgency_line = first_section_line(doc_text, "Urgency")
    last_line = first_section_line(doc_text, "Last Transpired")
    return {
        "open_items": open_items,
        "urgency": strip_markdown(urgency_line) or "P2 / Track",
        "last_transpired": strip_markdown(last_line) or f"{now_stamp()} - Local markdown update",
    }


def ensure_operational_labels(api: TrelloAPI, apply: bool) -> dict[str, str]:
    labels = api.get_labels()
    by_name = {label.get("name"): label for label in labels if label.get("name")}
    ids: dict[str, str] = {}
    for name, color in api.operational_labels.items():
        if name in by_name:
            ids[name] = by_name[name]["id"]
        elif apply:
            created = api.create_label(name, color)
            if created:
                ids[name] = created["id"]
                print(f"Created label: {name}")
        else:
            print(f"Would create label: {name}")
    return ids


def apply_desired_labels(
    api: TrelloAPI,
    card: dict[str, Any],
    desired: set[str],
    label_ids: dict[str, str],
    apply: bool,
) -> list[str]:
    existing_ids = set(card.get("idLabels") or [])
    changes = []
    for label_name in sorted(desired):
        label_id = label_ids.get(label_name)
        if not label_id or label_id in existing_ids:
            continue
        changes.append(f"add label {label_name}")
        if apply:
            api.add_label_to_card(card["id"], label_id)
            card.setdefault("idLabels", [])
            if label_id not in card["idLabels"]:
                card["idLabels"].append(label_id)
            card.setdefault("labels", [])
            if not any(label.get("id") == label_id for label in card["labels"]):
                card["labels"].append({"id": label_id, "name": label_name})
    return changes


def attach_snapshot(
    api: TrelloAPI,
    card: dict[str, Any],
    doc_path: Path,
    entry: dict[str, Any],
    apply: bool,
) -> tuple[str | None, list[str]]:
    if not api.attach_snapshots or not doc_path.exists():
        return entry.get("attachment_id"), []

    file_hash = sha256_file(doc_path)
    managed_ids = [
        attachment.get("id")
        for attachment in card.get("attachments", []) or []
        if (attachment.get("name") or "").startswith(MANAGED_ATTACHMENT_PREFIX)
    ]
    managed_ids = [attachment_id for attachment_id in managed_ids if attachment_id]
    current_id = entry.get("attachment_id")
    extra_ids = [attachment_id for attachment_id in managed_ids if attachment_id != current_id]

    if file_hash and file_hash == entry.get("attachment_hash") and current_id:
        changes = []
        if api.snapshot_policy == "latest_only" and extra_ids:
            changes.append("remove duplicate managed markdown snapshots")
            if apply:
                for attachment_id in extra_ids:
                    api.delete_attachment(card["id"], attachment_id)
        return current_id, changes

    changes = [f"attach markdown snapshot {rel(doc_path)}"]
    if api.snapshot_policy == "latest_only" and managed_ids:
        changes.append("replace previous managed markdown snapshot")
    if not apply:
        return entry.get("attachment_id"), changes

    if api.snapshot_policy == "latest_only":
        for attachment_id in managed_ids:
            api.delete_attachment(card["id"], attachment_id)
    elif current_id:
        api.delete_attachment(card["id"], current_id)

    attachment_name = f"{MANAGED_ATTACHMENT_PREFIX}{doc_path.name}"
    uploaded = api.attach_file(card["id"], doc_path, attachment_name)
    if uploaded:
        return uploaded.get("id"), changes
    return entry.get("attachment_id"), changes + ["attachment upload failed"]


def render_meaningful_comment(summary: dict[str, Any]) -> str:
    open_count = len(summary.get("open_items") or [])
    links = summary.get("key_links") or []
    first_link = f"\n- Key link: [{links[0]['label']}]({links[0]['url']})" if links else ""
    return textwrap.dedent(
        f"""\
        {MANAGED_COMMENT_PREFIX}

        - Urgency: {summary['urgency']}
        - Lane: {summary['lane']}
        - Next action: {summary['next_action']}
        - Open items: {open_count}{first_link}
        - Local doc: `{summary['local_path']}`
        """
    ).strip()


def maybe_comment_meaningful_change(
    api: TrelloAPI,
    card: dict[str, Any],
    entry: dict[str, Any],
    summary: dict[str, Any],
    digest: str,
    apply: bool,
) -> tuple[str | None, list[str]]:
    if not api.comments_enabled or api.comment_policy != "meaningful_changes":
        return entry.get("last_comment_digest"), []
    if not entry.get("comments_baselined"):
        return entry.get("last_comment_digest"), []
    previous_digest = entry.get("working_brief_digest")
    if not previous_digest or previous_digest == digest:
        return entry.get("last_comment_digest"), []

    comment = render_meaningful_comment(summary)
    comment_digest = sha256_text(comment)
    if entry.get("last_comment_digest") == comment_digest:
        return comment_digest, []

    changes = ["post meaningful-change Trello comment"]
    if apply:
        posted = api.add_comment(card["id"], comment)
        if not posted:
            changes.append("comment post failed")
            return entry.get("last_comment_digest"), changes
    return comment_digest, changes


def update_entry(
    ledger: dict[str, Any],
    classification: dict[str, Any],
    doc_path: Path,
    local_hash: str | None,
    attachment_id: str | None,
    attachment_hash: str | None,
    sync_status: str,
    working_brief_digest_value: str | None = None,
    last_comment_digest: str | None = None,
) -> None:
    card = classification["card"]
    local_id = classification.get("local_id")
    entry = ledger.setdefault("cards", {}).setdefault(card["id"], {})
    entry.update(
        {
            "card_id": card["id"],
            "short_link": card.get("shortLink"),
            "short_url": card.get("shortUrl"),
            "name": card.get("name"),
            "lane": classification.get("lane"),
            "list_id": card.get("idList"),
            "classification": classification.get("classification"),
            "local_id": local_id,
            "local_path": rel(doc_path),
            "confidence": round(float(classification.get("confidence", 0.0)), 3),
            "reason": classification.get("reason"),
            "trello_last_activity": card.get("dateLastActivity"),
            "trello_desc_hash": sha256_text(card.get("desc") or ""),
            "trello_state_hash": trello_state_hash(card),
            "local_hash": local_hash,
            "local_mtime": doc_path.stat().st_mtime if doc_path.exists() else None,
            "attachment_id": attachment_id,
            "attachment_hash": attachment_hash,
            "sync_status": sync_status,
            "synced_at": now_local().isoformat(),
        }
    )
    if working_brief_digest_value is not None:
        entry["working_brief_digest"] = working_brief_digest_value
        entry["comments_baselined"] = True
    if last_comment_digest is not None:
        entry["last_comment_digest"] = last_comment_digest
    if local_id:
        ledger.setdefault("tasks", {})[local_id] = card["id"]


def write_conflict(
    card: dict[str, Any],
    entry: dict[str, Any],
    reason: str,
    local_path: Path,
) -> Path:
    ensure_dirs()
    path = CONFLICTS_DIR / f"{today_slug()}-{card.get('shortLink', card['id'][:8])}.md"
    content = textwrap.dedent(
        f"""\
        # Trello Sync Conflict - {strip_markdown(card.get('name', 'Untitled'))}

        > **Detected:** {now_stamp()}
        > **Reason:** {reason}
        > **Trello:** [{card.get('shortUrl')}]({card.get('shortUrl')})
        > **Local doc:** `{rel(local_path)}`

        ## What Changed

        - Trello last activity: `{card.get('dateLastActivity')}`
        - Previous Trello activity: `{entry.get('trello_last_activity')}`
        - Local hash changed from ledger: `{entry.get('local_hash')}`

        ## Resolution

        Review the Trello card and local markdown file, then run:

        ```bash
        python3 system/scripts/trello_bridge.py sync --apply
        ```

        The bridge intentionally left this field unchanged rather than guessing.
        """
    )
    write_text(path, content)
    return path


def newest_changed_side(card: dict[str, Any], doc_path: Path) -> tuple[str | None, str]:
    if not doc_path.exists():
        return "trello", "Trello is newer because no local markdown exists"
    trello_dt = parse_trello_date(card.get("dateLastActivity"))
    if not trello_dt:
        return None, "cannot compare local and Trello timestamps"
    local_dt = dt.datetime.fromtimestamp(doc_path.stat().st_mtime).astimezone()
    delta = local_dt.timestamp() - trello_dt.timestamp()
    if abs(delta) <= 90:
        return None, "local and Trello timestamps are within the conflict window"
    if delta > 0:
        return "local", f"local markdown is newer ({local_dt.strftime('%Y-%m-%d %H:%M')})"
    return "trello", f"Trello is newer ({trello_dt.strftime('%Y-%m-%d %H:%M')})"


def sync_card(
    api: TrelloAPI,
    ledger: dict[str, Any],
    classification: dict[str, Any],
    label_ids: dict[str, str],
    apply: bool,
    actions_cache: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    card = classification["card"]
    doc_path = classification["local_path"]
    entry = ledger.get("cards", {}).get(card["id"], {})
    actions = actions_cache.setdefault(card["id"], api.get_card_actions(card["id"]))
    changes: list[str] = []
    status = "unchanged"

    if classification["classification"] == "needs_review":
        existing_doc = read_text(doc_path)
        review_doc = build_card_doc(card, classification, actions, existing_doc)
        changes = ["manual review required"]
        if review_doc.rstrip() != existing_doc.rstrip():
            changes.append(f"write review doc {rel(doc_path)}")
            if apply:
                write_text(doc_path, review_doc)
        local_hash = sha256_file(doc_path) if doc_path.exists() else None
        if apply:
            update_entry(
                ledger,
                classification,
                doc_path,
                local_hash,
                entry.get("attachment_id"),
                entry.get("attachment_hash"),
                "needs_review",
            )
        return {
            "card": card,
            "classification": classification,
            "status": "needs_review",
            "changes": changes,
            "urgency": urgency(card, classification["lane"]),
        }

    existing_doc = read_text(doc_path)
    local_hash_before = sha256_text(existing_doc) if existing_doc else None
    local_changed = bool(
        entry.get("local_hash")
        and local_hash_before
        and local_hash_before != entry.get("local_hash")
    )
    trello_changed = bool(
        entry.get("trello_state_hash")
        and trello_state_hash(card) != entry.get("trello_state_hash")
    )

    if local_changed and trello_changed:
        winner, reason = newest_changed_side(card, doc_path)
        if winner == "local":
            changes.append(f"newest-change-wins: {reason}")
            trello_changed = False
        elif winner == "trello":
            changes.append(f"newest-change-wins: {reason}")
            local_changed = False
        else:
            status = "conflict"
            changes.append(f"local and Trello changed since last sync; {reason}")
            if apply:
                conflict_path = write_conflict(
                    card,
                    entry,
                    "Both local markdown and Trello changed since the last sync.",
                    doc_path,
                )
                changes.append(f"wrote conflict {rel(conflict_path)}")
            update_entry(
                ledger,
                classification,
                doc_path,
                local_hash_before,
                entry.get("attachment_id"),
                entry.get("attachment_hash"),
                status,
            )
            return {
                "card": card,
                "classification": classification,
                "status": status,
                "changes": changes,
                "urgency": urgency(card, classification["lane"]),
            }

    working_summary: dict[str, Any] | None = None
    brief_digest: str | None = None
    comment_digest = entry.get("last_comment_digest")

    if local_changed and existing_doc:
        working_summary = working_brief_summary(card, classification, actions, doc_path, existing_doc)
        brief_digest = working_brief_digest(working_summary)
        new_desc = build_managed_desc(card, classification, actions, doc_path, doc_text=existing_doc)
        if new_desc != (card.get("desc") or ""):
            changes.append("push local markdown summary to Trello description")
            if apply:
                updated_card = api.update_card(card["id"], desc=new_desc)
                if isinstance(updated_card, dict):
                    card.update(updated_card)
                card["desc"] = new_desc
        status = "pushed_local"
    else:
        new_doc = build_local_doc(card, classification, actions, existing_doc)
        if new_doc.rstrip() != existing_doc.rstrip():
            changes.append(f"write local doc {rel(doc_path)}")
            if apply:
                write_text(doc_path, new_doc)
        working_summary = working_brief_summary(card, classification, actions, doc_path, new_doc)
        brief_digest = working_brief_digest(working_summary)
        new_desc = build_managed_desc(card, classification, actions, doc_path, doc_text=new_doc)
        if new_desc != (card.get("desc") or ""):
            changes.append("update Trello description managed block")
            if apply:
                updated_card = api.update_card(card["id"], desc=new_desc)
                if isinstance(updated_card, dict):
                    card.update(updated_card)
                card["desc"] = new_desc
        status = "pulled_trello" if trello_changed else ("created_or_refreshed" if changes else "unchanged")

    desired = desired_label_names(card, classification["lane"])
    changes.extend(apply_desired_labels(api, card, desired, label_ids, apply))

    if working_summary and brief_digest:
        comment_digest, comment_changes = maybe_comment_meaningful_change(
            api, card, entry, working_summary, brief_digest, apply
        )
        changes.extend(comment_changes)

    local_hash_after = sha256_file(doc_path) if doc_path.exists() else None
    attachment_id, attachment_changes = attach_snapshot(api, card, doc_path, entry, apply)
    changes.extend(attachment_changes)
    attachment_hash = sha256_file(doc_path) if doc_path.exists() else entry.get("attachment_hash")

    if apply:
        update_entry(
            ledger,
            classification,
            doc_path,
            local_hash_after,
            attachment_id,
            attachment_hash,
            status,
            brief_digest,
            comment_digest,
        )

    return {
        "card": card,
        "classification": classification,
        "status": status,
        "changes": changes,
        "urgency": urgency(card, classification["lane"]),
    }


def fetch_context(api: TrelloAPI) -> tuple[list[dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    lists = api.get_lists()
    cards = api.get_cards()
    lists_by_id = {item["id"]: item["name"] for item in lists}
    return cards, lists_by_id, lists


def classify_all(
    api: TrelloAPI,
    cards: list[dict[str, Any]],
    tasks: dict[str, dict[str, Any]],
    ledger: dict[str, Any],
) -> list[dict[str, Any]]:
    return [classify_card(api, card, tasks, ledger) for card in cards if not card.get("closed")]


def classification_summary(classifications: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in classifications:
        counts[item["classification"]] = counts.get(item["classification"], 0) + 1
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts)) or "no cards"


def print_classification_table(classifications: list[dict[str, Any]]) -> None:
    print("| Action | Lane | Card | Local | Confidence | Reason |")
    print("|:-------|:-----|:-----|:------|:-----------|:-------|")
    for item in classifications:
        card = item["card"]
        local = item.get("local_id") or rel(item["local_path"])
        print(
            "| {action} | {lane} | {card} | {local} | {confidence:.2f} | {reason} |".format(
                action=item["classification"],
                lane=item["lane"],
                card=strip_markdown(card.get("name", "")).replace("|", "/"),
                local=str(local).replace("|", "/"),
                confidence=float(item.get("confidence", 0.0)),
                reason=item.get("reason", ""),
            )
        )


def write_run_report(name: str, rows: list[dict[str, Any]], classifications: list[dict[str, Any]]) -> Path:
    ensure_dirs()
    stamp = now_local().strftime("%Y-%m-%d_%H%M%S")
    path = SYNC_RUNS_DIR / f"{stamp}_{name}.md"
    lines = [
        f"# Trello {name.title()} Run - {now_stamp()}",
        "",
        f"Summary: {classification_summary(classifications)}",
        "",
        "| Status | Card | Classification | Changes |",
        "|:-------|:-----|:---------------|:--------|",
    ]
    for row in rows:
        card = row["card"]
        lines.append(
            "| {status} | [{name}]({url}) | {classification} | {changes} |".format(
                status=row.get("status", ""),
                name=strip_markdown(card.get("name", "")).replace("|", "/"),
                url=card.get("shortUrl", ""),
                classification=row["classification"]["classification"],
                changes="<br>".join(row.get("changes") or ["none"]).replace("|", "/"),
            )
        )
    write_text(path, "\n".join(lines))
    return path


def build_hotlist(rows: list[dict[str, Any]]) -> str:
    eligible = [
        row
        for row in rows
        if row["classification"]["classification"] != "reference_only"
    ]
    eligible.sort(key=lambda row: row["urgency"]["score"], reverse=True)
    lines = [
        HOTLIST_BEGIN,
        "## Trello Hotlist",
        "",
        "> Managed by Trello bridge. Generated from Trello card lanes, labels, due dates, and open items.",
        "",
        "| Urgency | Card | Lane | Last Transpired | Open Items | Due | Labels |",
        "|:--------|:-----|:-----|:----------------|:-----------|:----|:-------|",
    ]
    for row in eligible[:12]:
        card = row["card"]
        item_count = len(checklist_open_items(card))
        labels = ", ".join(label.get("name") or label.get("color") or "" for label in card.get("labels", [])) or ""
        lines.append(
            "| {urgency} | [{name}]({url}) | {lane} | {last} | {items} | {due} | {labels} |".format(
                urgency=row["urgency"]["label"],
                name=strip_markdown(card.get("name", "")).replace("|", "/"),
                url=card.get("shortUrl", ""),
                lane=row["classification"]["lane"],
                last=fmt_date(card.get("dateLastActivity")),
                items=item_count,
                due=fmt_date(card.get("due")),
                labels=labels.replace("|", "/"),
            )
        )
    lines.append(HOTLIST_END)
    return "\n".join(lines)


def update_task_master_hotlist(rows: list[dict[str, Any]], apply: bool) -> list[str]:
    if not TASK_MASTER_PATH.exists():
        return ["TASK_MASTER.md not found"]
    content = read_text(TASK_MASTER_PATH)
    hotlist = build_hotlist(rows)
    updated = replace_block(content, HOTLIST_BEGIN, HOTLIST_END, hotlist)
    if updated != content:
        if apply:
            write_text(TASK_MASTER_PATH, updated)
        return ["update TASK_MASTER Trello hotlist"]
    return []


def run_bootstrap(apply: bool) -> int:
    api = TrelloAPI()
    ledger = load_ledger()
    tasks = load_task_master_tasks()
    cards, _lists_by_id, _lists = fetch_context(api)
    classifications = classify_all(api, cards, tasks, ledger)

    print(f"Bootstrap {'apply' if apply else 'dry-run'}: {classification_summary(classifications)}")
    print_classification_table(classifications)

    if not apply:
        print("\nNo writes performed. Run with --apply to write docs, ledger, Trello descriptions, labels, and snapshots.")
        return 0

    ensure_dirs()
    label_ids = ensure_operational_labels(api, apply=True)
    actions_cache: dict[str, list[dict[str, Any]]] = {}
    rows = [
        sync_card(api, ledger, item, label_ids, apply=True, actions_cache=actions_cache)
        for item in classifications
    ]
    rows.append(
        {
            "card": {"name": "TASK_MASTER hotlist", "shortUrl": ""},
            "classification": {"classification": "local"},
            "status": "local",
            "changes": update_task_master_hotlist(rows, apply=True),
            "urgency": {"score": 0, "label": ""},
        }
    )
    save_ledger(ledger)
    report = write_run_report("bootstrap", rows, classifications)
    print(f"\nBootstrap applied. Report: {rel(report)}")
    return 0


def run_sync(apply: bool, quiet: bool = False) -> int:
    api = TrelloAPI()
    if quiet and not within_workday(api):
        return 0
    ledger = load_ledger()
    tasks = load_task_master_tasks()
    cards, _lists_by_id, _lists = fetch_context(api)
    classifications = classify_all(api, cards, tasks, ledger)
    label_ids = ensure_operational_labels(api, apply=apply)
    actions_cache: dict[str, list[dict[str, Any]]] = {}

    rows = [
        sync_card(api, ledger, item, label_ids, apply=apply, actions_cache=actions_cache)
        for item in classifications
    ]
    hotlist_changes = update_task_master_hotlist(rows, apply=apply)
    if hotlist_changes:
        rows.append(
            {
                "card": {"name": "TASK_MASTER hotlist", "shortUrl": ""},
                "classification": {"classification": "local"},
                "status": "local",
                "changes": hotlist_changes,
                "urgency": {"score": 0, "label": ""},
            }
        )

    if apply:
        save_ledger(ledger)
        report = write_run_report("sync", rows, classifications)
    else:
        report = None

    if not quiet:
        print(f"Sync {'apply' if apply else 'dry-run'}: {classification_summary(classifications)}")
        for row in rows:
            changes = row.get("changes") or []
            if changes:
                print(f"- {row['status']}: {row['card'].get('name')} -> {', '.join(changes)}")
        if report:
            print(f"Report: {rel(report)}")
        if not apply:
            print("No writes performed. Run with --apply to update Trello and local markdown.")
    return 0


def run_status() -> int:
    api = TrelloAPI()
    ledger = load_ledger()
    tasks = load_task_master_tasks()
    cards, _lists_by_id, lists = fetch_context(api)
    classifications = classify_all(api, cards, tasks, ledger)
    by_list = {item["name"]: 0 for item in lists}
    for item in classifications:
        list_name = next((lst["name"] for lst in lists if lst["id"] == item["card"].get("idList")), item["lane"])
        by_list[list_name] = by_list.get(list_name, 0) + 1
    print("Trello bridge status")
    print(f"- Board cards: {len(cards)}")
    print(f"- Local TASK_MASTER tasks parsed: {len(tasks)}")
    print(f"- Ledger cards: {len(ledger.get('cards', {}))}")
    print(f"- Classification: {classification_summary(classifications)}")
    print("- Lists:")
    for name, count in by_list.items():
        print(f"  - {name}: {count}")
    needs_review = [item for item in classifications if item["classification"] == "needs_review"]
    if needs_review:
        print("- Needs review:")
        for item in needs_review:
            print(f"  - {item['card'].get('name')} ({item['reason']}, score={item['confidence']:.2f})")
    return 0


def within_workday(api: TrelloAPI) -> bool:
    config = api.config.get("workday_sync", {})
    if not config.get("enabled", True):
        return True
    current = now_local()
    if current.weekday() not in set(config.get("weekdays", [0, 1, 2, 3, 4])):
        return False
    start = config.get("start", "07:00")
    end = config.get("end", "18:30")
    now_hm = current.strftime("%H:%M")
    return start <= now_hm <= end


def install_agent(load: bool = False) -> int:
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents / "com.beatspm.trello-sync.plist"
    python = sys.executable or "/usr/bin/python3"
    command = (
        f"cd {shlex.quote(str(BASE_DIR))} && "
        f"{shlex.quote(python)} system/scripts/trello_bridge.py sync --apply --quiet"
    )
    plist = {
        "Label": "com.beatspm.trello-sync",
        "ProgramArguments": ["/bin/zsh", "-lc", command],
        "StartInterval": 1800,
        "WorkingDirectory": str(BASE_DIR),
        "StandardOutPath": str(TRELLO_DIR / "trello-sync.out.log"),
        "StandardErrorPath": str(TRELLO_DIR / "trello-sync.err.log"),
        "RunAtLoad": True,
    }
    ensure_dirs()
    plist_path.write_bytes(plistlib.dumps(plist))
    print(f"Installed LaunchAgent: {plist_path}")
    if load:
        subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
        subprocess.run(["launchctl", "load", str(plist_path)], check=False)
        print("LaunchAgent loaded.")
    else:
        print(f"Load it with: launchctl load {plist_path}")
    return 0


def uninstall_agent() -> int:
    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.beatspm.trello-sync.plist"
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
        plist_path.unlink()
        print(f"Removed LaunchAgent: {plist_path}")
    else:
        print("LaunchAgent is not installed.")
    return 0


def attach_to_task(task_id: str, filepath: str) -> int:
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return 1
    ledger = load_ledger()
    card_id = ledger.get("tasks", {}).get(task_id)
    if not card_id:
        for candidate_id, entry in ledger.get("cards", {}).items():
            if entry.get("local_id") == task_id or candidate_id == task_id:
                card_id = candidate_id
                break
    if not card_id:
        print(f"{task_id} not found in Trello ledger. Run bootstrap or sync first.")
        return 1
    api = TrelloAPI()
    result = api.attach_file(card_id, path)
    if result:
        print(f"Attached {path.name} to {task_id}.")
        return 0
    print("Attachment failed.")
    return 1


def print_lists() -> int:
    api = TrelloAPI()
    lists = api.get_lists()
    trimmed = [
        {
            "id": item.get("id"),
            "name": item.get("name"),
            "pos": item.get("pos"),
            "closed": item.get("closed"),
        }
        for item in lists
    ]
    print(json.dumps(trimmed, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize Beats PM markdown with Trello.")
    subparsers = parser.add_subparsers(dest="command")

    bootstrap = subparsers.add_parser("bootstrap", help="Reconcile existing Trello cards.")
    bootstrap.add_argument("--dry-run", action="store_true", help="Preview reconciliation without writes.")
    bootstrap.add_argument("--apply", action="store_true", help="Write reconciliation changes.")

    sync = subparsers.add_parser("sync", help="Run recurring sync.")
    sync.add_argument("--dry-run", action="store_true", help="Preview sync without writes.")
    sync.add_argument("--apply", action="store_true", help="Write sync changes.")
    sync.add_argument("--quiet", action="store_true", help="Only print errors; intended for LaunchAgent.")

    subparsers.add_parser("status", help="Show board/local sync status.")
    subparsers.add_parser("lists", help="Print Trello list IDs.")

    attach = subparsers.add_parser("attach", help="Attach a local file to a synced Trello card.")
    attach.add_argument("task_id")
    attach.add_argument("filepath")

    install = subparsers.add_parser("install-agent", help="Install 30-minute local LaunchAgent.")
    install.add_argument("--load", action="store_true", help="Load LaunchAgent immediately.")

    subparsers.add_parser("uninstall-agent", help="Unload and remove local LaunchAgent.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "sync"

    if command == "bootstrap":
        return run_bootstrap(apply=bool(args.apply and not args.dry_run))
    if command == "sync":
        return run_sync(apply=bool(args.apply and not args.dry_run), quiet=args.quiet)
    if command == "status":
        return run_status()
    if command == "lists":
        return print_lists()
    if command == "attach":
        return attach_to_task(args.task_id, args.filepath)
    if command == "install-agent":
        return install_agent(load=args.load)
    if command == "uninstall-agent":
        return uninstall_agent()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
