#!/usr/bin/env python3
"""Unified fast intake pipeline for single communication evidence.

This script implements the "Fast Single-Evidence Path" for communication intake
(screenshots, chat excerpts, pasted emails) in a single deterministic, token-efficient
Python run:

1. Ingests structured extraction data (JSON payload, file, stdin, or CLI flags).
2. Generates the standard communication transcript (3. Meetings/chat-transcripts/{platform}/).
3. Generates platform & chat run reports (3. Meetings/reports/{platform}-runs/ and chat-runs/).
4. Updates or creates the canonical task note (5. Trackers/tasks/{slug}.md).
5. Updates or creates stakeholder profiles (4. People/{slug}.md and 4. People/PEOPLE.md).
6. Updates or creates workstream notes (5. Trackers/workstreams/{slug}.md).
7. Records the intake run in the manifest (3. Meetings/chat-transcripts/_manifest.json).
8. Rebuilds Task Master, applies workstream MOC evidence links, and updates task triage.
9. Returns structured JSON with preview links and ready-to-display workstream snapshot.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
DEFAULT_ROOT = SYSTEM_ROOT.parent

if str(DEFAULT_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_ROOT))

from system.scripts import chat_intake_state, markdown_humanizer, task_store
from system.scripts.preview_link import to_url, needs_staging, stage_copy


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def slugify(text: str, fallback: str = "item") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned or fallback


def find_next_task_number(root: Path, prefix: str) -> int:
    tasks_dir = root / "5. Trackers" / "tasks"
    if not tasks_dir.exists():
        return 1
    prefix_clean = prefix.strip().upper()
    pattern = re.compile(rf"^{prefix_clean}-(\d+)", re.IGNORECASE)
    highest = 0
    for file in tasks_dir.glob("*.md"):
        if file.name.startswith("_"):
            continue
        try:
            content = file.read_text(encoding="utf-8", errors="replace")[:1000]
            m = re.search(r"^task_id:\s*['\"]?([A-Za-z0-9_-]+)['\"]?", content, re.MULTILINE)
            if m:
                tid = m.group(1)
                pm = pattern.match(tid)
                if pm:
                    num = int(pm.group(1))
                    if num > highest:
                        highest = num
            # Also check file stem
            sm = pattern.match(file.stem)
            if sm:
                num = int(sm.group(1))
                if num > highest:
                    highest = num
        except Exception:
            continue
    return highest + 1


def get_preview_url(path: Path) -> str:
    target = stage_copy(path) if needs_staging(path) else path
    return to_url(target)


@dataclass
class CommunicationIntakeResult:
    ok: bool
    run_id: str
    platform: str
    scope: str
    task_id: str
    task_title: str
    task_path: str
    transcript_path: str
    run_report_path: str
    chat_report_path: str
    stakeholder_path: str | None = None
    workstream_path: str | None = None
    preview_links: dict[str, str] = field(default_factory=dict)
    workstream_snapshot: str = ""
    issues: list[str] = field(default_factory=list)


def process_communication_intake(
    payload: dict[str, Any],
    root: Path | None = None,
) -> CommunicationIntakeResult:
    root = (root or DEFAULT_ROOT).resolve()
    issues: list[str] = []

    platform = str(payload.get("platform", "teams")).strip().lower()
    scope = str(payload.get("scope", "general")).strip()
    scope_slug = slugify(scope, fallback="general")
    sender = str(payload.get("sender", "Unknown")).strip()
    extracted_text = str(payload.get("extracted_text", "")).strip()
    timestamp_str = payload.get("timestamp")
    
    if timestamp_str:
        try:
            timestamp = dt.datetime.fromisoformat(timestamp_str)
        except Exception:
            timestamp = now_local()
    else:
        timestamp = now_local()

    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H:%M")
    run_id = str(payload.get("run_id") or f"run-{platform}-{scope_slug[:20]}-{timestamp.strftime('%Y%m%d%H%M%S')}")

    # 1. Resolve Task Metadata
    task_info = payload.get("task", {})
    task_title = str(task_info.get("title") or f"Communication follow-up: {scope}").strip()
    if task_info.get("slug"):
        task_slug = str(task_info["slug"]).strip()
    else:
        raw_slug = task_store.human_slug(task_title)
        words = raw_slug.split("-")[:5]
        while len(words) > 1 and words[-1] in {"with", "and", "to", "for", "in", "on", "at", "by", "of", "from", "the", "a"}:
            words.pop()
        task_slug = "-".join(words) or "task"
    prefix = str(task_info.get("prefix", "CAPT")).strip().upper()
    
    explicit_task_id = task_info.get("task_id")
    if explicit_task_id:
        task_id = str(explicit_task_id).strip()
    else:
        next_num = find_next_task_number(root, prefix)
        task_id = f"{prefix}-{next_num:03d}-{task_slug}"

    owner = str(task_info.get("owner", "Ernesto Rodriguez")).strip()
    due = str(task_info.get("due", (timestamp.date() + dt.timedelta(days=5)).isoformat())).strip()
    lane = str(task_info.get("lane", "next")).strip()
    priority = str(task_info.get("priority", "next")).strip()
    workstream_slug = str(task_info.get("workstream") or payload.get("workstream", {}).get("slug", "unassigned")).strip()

    # 2. File Paths
    transcript_rel = Path(f"3. Meetings/chat-transcripts/{platform}/{date_str}_{scope_slug}_{run_id}.md")
    run_report_rel = Path(f"3. Meetings/reports/{platform}-runs/{run_id}.md")
    chat_report_rel = Path(f"3. Meetings/reports/chat-runs/{run_id}.md")
    task_rel = Path(f"5. Trackers/tasks/{task_slug}.md")
    
    transcript_abs = root / transcript_rel
    run_report_abs = root / run_report_rel
    chat_report_abs = root / chat_report_rel
    task_abs = root / task_rel

    transcript_abs.parent.mkdir(parents=True, exist_ok=True)
    run_report_abs.parent.mkdir(parents=True, exist_ok=True)
    chat_report_abs.parent.mkdir(parents=True, exist_ok=True)
    task_abs.parent.mkdir(parents=True, exist_ok=True)

    # 3. Handle Stakeholder
    stakeholder_info = payload.get("stakeholder")
    stakeholder_rel: Path | None = None
    if stakeholder_info and isinstance(stakeholder_info, dict) and stakeholder_info.get("name"):
        s_name = str(stakeholder_info["name"]).strip()
        s_slug = slugify(s_name)
        s_role = str(stakeholder_info.get("role", "Team Member")).strip()
        s_org = str(stakeholder_info.get("org", "Captios Partners")).strip()
        s_notes = str(stakeholder_info.get("notes", "")).strip()
        stakeholder_rel = Path(f"4. People/{s_slug}.md")
        stakeholder_abs = root / stakeholder_rel
        stakeholder_abs.parent.mkdir(parents=True, exist_ok=True)

        if not stakeholder_abs.exists():
            profile_content = f"""---
title: {s_name}
role: {s_role}
organization: {s_org}
client: Internal
email: ""
status: active
tags: [team, captios, stakeholder]
---

# {s_name}

> **Role**: {s_role}, {s_org}  
> **Key Focus**: {s_notes or f'Collaboration and onboarding in {scope}'}  

---

## Technical & Collaboration Context

- **Organization**: {s_org}
- **Primary Scope**: {scope}
- **Active Focus**: {s_notes or 'Active project engagement'}

---

## Active Commitments & Interactions

- **{date_str} ({platform.capitalize()} `{scope}`)**: Interaction logged via intake run `{run_id}`.
- **Action Items**:
  - `{task_id}`: {task_title}
"""
            markdown_humanizer.write_generated_markdown(stakeholder_abs, profile_content)
        else:
            # Append interaction note if not present
            existing_p = stakeholder_abs.read_text(encoding="utf-8", errors="replace")
            if task_id not in existing_p:
                append_note = f"\n- **{date_str} ({platform.capitalize()} `{scope}`)**: Action `{task_id}` ({task_title}).\n"
                stakeholder_abs.write_text(existing_p.rstrip() + "\n" + append_note, encoding="utf-8")

        # Update 4. People/PEOPLE.md if needed
        people_index = root / "4. People" / "PEOPLE.md"
        if people_index.exists():
            people_txt = people_index.read_text(encoding="utf-8", errors="replace")
            if s_name not in people_txt:
                row = f"| **{s_name}** | {s_role} | {s_notes or f'{scope} lead'} |\n"
                # Insert below the first table found or Captios team
                marker = "## Captios Partners (Consulting Team)"
                if marker in people_txt:
                    idx = people_txt.find(marker)
                    tbl_end = people_txt.find("\n\n---", idx)
                    if tbl_end != -1:
                        new_txt = people_txt[:tbl_end].rstrip() + "\n" + row + people_txt[tbl_end:]
                        people_index.write_text(new_txt, encoding="utf-8")

    # 4. Handle Workstream Note
    workstream_info = payload.get("workstream")
    workstream_rel: Path | None = None
    if workstream_info and isinstance(workstream_info, dict) and workstream_info.get("slug"):
        ws_slug = slugify(workstream_info["slug"])
        ws_title = str(workstream_info.get("title", f"Workstream — {ws_slug}")).strip()
        ws_client = str(workstream_info.get("client", "Captios Partners")).strip()
        workstream_rel = Path(f"5. Trackers/workstreams/{ws_slug}.md")
        workstream_abs = root / workstream_rel
        workstream_abs.parent.mkdir(parents=True, exist_ok=True)

        if not workstream_abs.exists():
            ws_content = f"""---
title: '{ws_title}'
workstream: '{ws_slug}'
client: '{ws_client}'
alias: '{ws_slug}'
type: workstream
status: active
---

# {ws_title}

> {workstream_info.get('summary', f'Workstream for {ws_title}.')}

## Engagement Summary

- **Client / Organization**: {ws_client}
- **Lead**: {owner}
- **Channel / Scope**: `{scope}`
- **Status**: Active / In Progress

## Key Objectives & Scope

1. Deliver key objectives for {ws_title}.
2. Ensure cross-team alignment and weekly cadence.

## Recent Evidence & Transcripts

- [[{transcript_rel.stem}|{transcript_rel.as_posix()}]]: Evidence captured from {platform} on {date_str}.

<!-- BEGIN AUTO-EVIDENCE (managed by workstream_moc.py) -->
<!-- END AUTO-EVIDENCE -->
"""
            markdown_humanizer.write_generated_markdown(workstream_abs, ws_content)

    # 5. Write Canonical Task Note
    summary_text = str(task_info.get("summary") or extracted_text or task_title)
    context_text = str(task_info.get("context") or f"{sender} posted in {platform} ({scope}) at {time_str} on {date_str}: \"{extracted_text}\"")
    next_actions_raw = task_info.get("next_actions") or [
        f"Await or initiate scheduling with {sender} in `{scope}`",
        f"Confirm scope and weekly allocation for {workstream_slug}",
        f"Complete scheduled walkthrough and align next steps"
    ]
    if isinstance(next_actions_raw, str):
        next_actions = [next_actions_raw]
    else:
        next_actions = list(next_actions_raw)

    next_actions_md = "\n".join(f"- [ ] {act.rstrip('.')}." for act in next_actions)

    task_content = f"""---
title: '{task_title}'
task_id: {task_id}
status: open
lane: {lane}
workstream: {workstream_slug}
created: {date_str}
updated: {date_str}
source_refs:
  - {transcript_rel.as_posix()}
inferred_fields:
  - due
tags: [beats-task, {workstream_slug}, {lane}]
priority: {priority}
due: {due}
owner: {owner}
---

# {task_title}

## Summary

{summary_text}

## Context

{context_text}

## Success and scope

- Complete initial alignment and scope definition with {sender}.
- Ensure workstream commitments and dates are clearly defined.

## Next actions

{next_actions_md}

## Evidence

- `{transcript_rel.as_posix()}`

## Progress

| Date | Source | Update |
|:---|:---|:---|
| {date_str} | {platform.capitalize()} ({scope}) | Intake logged from message by {sender}. |

## Decisions

- No decision recorded yet.
"""
    markdown_humanizer.write_generated_markdown(task_abs, task_content)

    # 6. Write Communication Transcript
    transcript_content = f"""# Communication Transcript — {platform} — {scope_slug}

**Date Captured**: {date_str} {time_str}
**Run ID**: {run_id}
**Platform**: {platform.capitalize()}
**Scope**: {scope}
**Effective Window**: user-provided evidence
**Read Policy**: Read-only; no send or mutation actions.
**Unread Policy**: No intentional read/unread mutation.

## Source References
- **Platform**: {platform.capitalize()}
- **Scope / Channel**: `{scope}`
- **Message Timestamp**: {time_str} ({date_str})
- **Sender**: {sender}
- **Raw Evidence Snippet**: {extracted_text}

## Atlassian References
- None referenced in visible evidence.

## Extracted Text (user-provided evidence only)
- {extracted_text}

## Evidence Snippets
- `{sender} ({time_str})`: "{extracted_text}"

## Candidate Tasks
| Status | Owner | Due | Task | Evidence |
| --- | --- | --- | --- | --- |
| open | {owner} | {due} | {task_title} (`{task_id}`) | {sender} message in {platform} `{scope}` |

## Decisions / Status Changes
- Action item captured: `{task_id}`.
- Workstream routed to `{workstream_slug}`.

## Routed Updates
- `{task_rel.as_posix()}`: Created canonical task note.
"""
    if stakeholder_rel:
        transcript_content += f"- `{stakeholder_rel.as_posix()}`: Stakeholder profile updated.\n"
    if workstream_rel:
        transcript_content += f"- `{workstream_rel.as_posix()}`: Workstream record linked.\n"

    transcript_content += f"""
## Issues And Recommendations
- Intake processed via automated single-evidence communication pipeline.
"""
    for signal in payload.get("peripheral_signals", []):
        transcript_content += f"- Peripheral Signal: {signal}\n"

    transcript_content += f"""
## Manual Follow-Ups
- Optional: Reply to {sender} in thread to confirm receipt and alignment.

## Safety Confirmation
- No source-system messages, emails, or calendar invites were sent.
- No source-system mutation tools were used.
- Unread state was not intentionally changed.
"""
    markdown_humanizer.write_generated_markdown(transcript_abs, transcript_content)

    # 7. Write Platform Run Report
    run_report_content = f"""---
title: {platform.capitalize()} Run Report - {task_title}
date: "{date_str}"
run_id: "{run_id}"
platform: "{platform}"
scope: "{scope_slug}"
status: "completed"
---

# {platform.capitalize()} Run Report: {task_title}

> **Run ID**: `{run_id}`  
> **Platform**: {platform.capitalize()}  
> **Scope**: `{scope}`  
> **Intake Mode**: Fast Single-Evidence Path (Automated Pipeline)  
> **Status**: ✅ Completed  

---

## 1. Scope & Operations

- **Platform & Scope**: {platform.capitalize()} > `{scope}`
- **Read-Only Operation**: User-provided evidence extraction (no source-system mutation).
- **Sender**: {sender} ({date_str} {time_str})
- **Message**: *"{extracted_text}"*

---

## 2. Workstream Finding & Candidate Tasks

- **Workstream**: `{workstream_slug}`
- **Authority Tier**: Standard / Product Lead
- **Commitment Type**: Internal / Collaborative
- **Completion State**: Open
- **Accepted Task**:
  - `{task_id}`: {task_title}
    - **Owner**: {owner}
    - **Due**: {due}
    - **Lane**: `{lane}` | **Priority**: `{priority}`

---

## 3. Workstream Snapshot

### {workstream_info.get('title', workstream_slug) if workstream_info else workstream_slug} (`{workstream_slug}`)
- **Latest outcome**: Communication logged from {sender}; next action scheduled
  - **Evidence**: {platform.capitalize()} `{scope}` ({date_str} {time_str})
- **Completed**: Evidence archived and tracked locally
  - **Completed**: {date_str} from intake
- **Open items**: 1
  - {owner} — {task_title} by {due} (`{task_id}`)
- **Recommended next 3**:
  - Await or initiate coordination with {sender}
  - Align workstream milestones and capacity
  - Complete initial sync walkthrough

---

## 4. Routed Updates

- `{transcript_rel.as_posix()}`
- `{run_report_rel.as_posix()}`
- `{chat_report_rel.as_posix()}`
- `{task_rel.as_posix()}`
"""
    if stakeholder_rel:
        run_report_content += f"- `{stakeholder_rel.as_posix()}`\n"
    if workstream_rel:
        run_report_content += f"- `{workstream_rel.as_posix()}`\n"

    run_report_content += f"""
---

## 5. Items Needing Manual Follow-Up

- Optional: Send confirmation to {sender} in {platform} thread.
"""
    for signal in payload.get("peripheral_signals", []):
        run_report_content += f"- Peripheral Observation: {signal}\n"

    run_report_content += """
---

## 6. Safety Confirmation

- ✅ No source-system messages, replies, or reactions were sent.
- ✅ No tenant or cloud platform state was mutated.
- ✅ Unread status across channels and chats was preserved.
"""
    markdown_humanizer.write_generated_markdown(run_report_abs, run_report_content)

    # 8. Write Unified Chat Run Report
    chat_report_content = f"""---
title: Chat Run Report - {task_title}
date: "{date_str}"
run_id: "{run_id}"
platform: "{platform}"
scope: "{scope_slug}"
status: "completed"
---

# Chat Run Report: {task_title}

> **Run ID**: `{run_id}`  
> **Platform**: {platform.capitalize()}  
> **Scope**: `{scope}`  
> **Transcript**: `{transcript_rel.as_posix()}`  
> **Report**: `{run_report_rel.as_posix()}`  
> **Status**: ✅ Completed  

---

## Summary
Extracted work signal from user-provided {platform} evidence in `{scope}`. Created task `{task_id}`, updated stakeholder profiles, and refreshed Task Master and workstream MOCs.
"""
    markdown_humanizer.write_generated_markdown(chat_report_abs, chat_report_content)

    # 9. Record Manifest Run
    try:
        manifest_args = argparse.Namespace(
            repo=str(root),
            manifest=None,
            platform=platform,
            scope=scope,
            run_id=run_id,
            latest_source_timestamp=timestamp.isoformat(),
            transcript_path=[transcript_rel.as_posix()],
            run_report_path=[run_report_rel.as_posix()],
        )
        with contextlib.redirect_stdout(io.StringIO()):
            chat_intake_state.command_record(manifest_args)
    except Exception as e:
        issues.append(f"Manifest record warning: {e}")

    # 10. Rebuild & Triangulate
    try:
        task_store.rebuild_task_master(root)
    except Exception as e:
        issues.append(f"Task Master rebuild warning: {e}")

    try:
        subprocess.run(
            [sys.executable, str(SYSTEM_ROOT / "scripts" / "workstream_moc.py"), "--apply"],
            cwd=str(root),
            capture_output=True,
            check=False,
        )
    except Exception as e:
        issues.append(f"Workstream MOC warning: {e}")

    try:
        subprocess.run(
            [
                sys.executable,
                str(SYSTEM_ROOT / "scripts" / "task_master_triage.py"),
                "--apply",
                "--touched-task",
                task_id,
            ],
            cwd=str(root),
            capture_output=True,
            check=False,
        )
    except Exception as e:
        issues.append(f"Task triage warning: {e}")

    # 11. Compile Preview Links
    preview_links = {
        "Transcript": get_preview_url(transcript_abs),
        "Run Report": get_preview_url(run_report_abs),
        "Task Detail": get_preview_url(task_abs),
    }
    if stakeholder_rel:
        preview_links["Stakeholder Profile"] = get_preview_url(root / stakeholder_rel)
    if workstream_rel:
        preview_links["Workstream"] = get_preview_url(root / workstream_rel)
    preview_links["Task Master"] = get_preview_url(root / "5. Trackers" / "TASK_MASTER.md")

    # 12. Build Workstream Snapshot Text
    ws_display = workstream_info.get("title", workstream_slug) if workstream_info else workstream_slug
    snapshot_lines = [
        f"### {ws_display} (`{workstream_slug}`)",
        f"- **Latest outcome**: Communication logged from {sender}; next action scheduled",
        f"  - **Evidence**: {platform.capitalize()} `{scope}` ({date_str} {time_str})",
        f"- **Completed**: Evidence archived and tracked locally",
        f"  - **Completed**: {date_str} from intake",
        f"- **Open items**: 1",
        f"  - {owner} — {task_title} by {due} (`{task_id}`)",
        f"- **Recommended next 3**:",
        f"  - Await or initiate scheduling with {sender} in `{scope}`",
        f"  - Confirm scope and weekly PM allocation for `{workstream_slug}`",
        f"  - Complete scheduled walkthrough and align next steps",
    ]
    snapshot_text = "\n".join(snapshot_lines)

    return CommunicationIntakeResult(
        ok=True,
        run_id=run_id,
        platform=platform,
        scope=scope,
        task_id=task_id,
        task_title=task_title,
        task_path=task_rel.as_posix(),
        transcript_path=transcript_rel.as_posix(),
        run_report_path=run_report_rel.as_posix(),
        chat_report_path=chat_report_rel.as_posix(),
        stakeholder_path=stakeholder_rel.as_posix() if stakeholder_rel else None,
        workstream_path=workstream_rel.as_posix() if workstream_rel else None,
        preview_links=preview_links,
        workstream_snapshot=snapshot_text,
        issues=issues,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic single-evidence communication intake pipeline")
    parser.add_argument("--repo", default=str(DEFAULT_ROOT), help="Repo root directory")
    parser.add_argument("--payload", help="JSON payload string")
    parser.add_argument("--file", help="Path to JSON payload file")
    parser.add_argument("--platform", default="teams", help="Communication platform (teams, slack, outlook, calendar)")
    parser.add_argument("--scope", default="", help="Channel/chat scope")
    parser.add_argument("--sender", default="", help="Message sender")
    parser.add_argument("--text", default="", help="Extracted verbatim text")
    parser.add_argument("--task-title", default="", help="Title for candidate task")
    parser.add_argument("--task-prefix", default="CAPT", help="Task ID prefix (e.g. CAPT, PROP)")
    parser.add_argument("--task-owner", default="Ernesto Rodriguez", help="Task owner")
    parser.add_argument("--task-due", default="", help="Task due date (YYYY-MM-DD)")
    parser.add_argument("--task-lane", default="next", help="Task lane (today, next, later)")
    parser.add_argument("--workstream-slug", default="", help="Workstream slug")
    parser.add_argument("--workstream-title", default="", help="Workstream display title")
    parser.add_argument("--stakeholder-name", default="", help="Stakeholder name")
    parser.add_argument("--stakeholder-role", default="", help="Stakeholder role")
    parser.add_argument("--stakeholder-org", default="Captios Partners", help="Stakeholder organization")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    payload: dict[str, Any] = {}
    if args.payload:
        payload = json.loads(args.payload)
    elif args.file:
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    elif not sys.stdin.isatty():
        stdin_txt = sys.stdin.read().strip()
        if stdin_txt:
            try:
                payload = json.loads(stdin_txt)
            except json.JSONDecodeError:
                payload = {"extracted_text": stdin_txt}

    # Merge CLI flags as overrides or defaults
    if args.platform:
        payload.setdefault("platform", args.platform)
    if args.scope:
        payload["scope"] = args.scope
    if args.sender:
        payload["sender"] = args.sender
    if args.text:
        payload["extracted_text"] = args.text

    task = payload.setdefault("task", {})
    if args.task_title:
        task["title"] = args.task_title
    if args.task_prefix:
        task["prefix"] = args.task_prefix
    if args.task_owner:
        task["owner"] = args.task_owner
    if args.task_due:
        task["due"] = args.task_due
    if args.task_lane:
        task["lane"] = args.task_lane
    if args.workstream_slug:
        task["workstream"] = args.workstream_slug

    if args.stakeholder_name:
        s = payload.setdefault("stakeholder", {})
        s["name"] = args.stakeholder_name
        if args.stakeholder_role:
            s["role"] = args.stakeholder_role
        if args.stakeholder_org:
            s["org"] = args.stakeholder_org

    if args.workstream_slug:
        ws = payload.setdefault("workstream", {})
        ws["slug"] = args.workstream_slug
        if args.workstream_title:
            ws["title"] = args.workstream_title

    root = Path(args.repo)
    result = process_communication_intake(payload, root=root)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(result.workstream_snapshot)
        print("\n---")
        print(f"Task ID: {result.task_id} ({result.task_path})")
        print(f"Transcript: {result.transcript_path}")
        print(f"Run Report: {result.run_report_path}")
        if result.stakeholder_path:
            print(f"Stakeholder: {result.stakeholder_path}")
        if result.workstream_path:
            print(f"Workstream: {result.workstream_path}")
        print("\nPreview Links:")
        for label, url in result.preview_links.items():
            print(f"  - {label}: {url}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
