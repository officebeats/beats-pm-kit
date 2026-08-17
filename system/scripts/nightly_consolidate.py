#!/usr/bin/env python3
"""Nightly sleep-time consolidation runner for Beats PM Kit.

Runs, in order, with each step isolated so one failure never aborts the rest:

1. ``context-index``   — force rebuild of the context-router index.
2. ``task-master``     — rebuild TASK_MASTER.md and normalize task status
                         frontmatter via ``task_store``.
3. ``humanizer``       — apply the markdown humanizer pass.
4. ``archive-check``   — report-only hygiene counts: active tasks whose status
                         is already done, and archived task notes whose status
                         is still open. Never moves or edits files.
5. ``day-skeleton``    — regenerate ``.beats/day_skeleton.md`` deterministically
                         (skip with ``--skip-skeleton``).

The JSON summary — ``{ok, ts, steps: [{step, ok, detail, wall_ms}]}`` — is
written to ``.beats/nightly-last-run.json``. Exit code is 0 only when every
step succeeded.

CLI: ``python3 -m system.scripts.nightly_consolidate [--json] [--skip-skeleton]``

Scheduling (opt-in): ``--install-launchd`` renders
``system/config/com.beats.nightly-consolidate.plist.template`` (substituting
``__REPO_ROOT__`` with this checkout) to
``~/Library/LaunchAgents/com.beats.nightly-consolidate.plist`` and prints the
``launchctl load`` command WITHOUT executing it. Nothing runs at 05:30 until
the user loads the agent themselves.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.scripts import context_router, day_skeleton, markdown_humanizer, task_store  # noqa: E402
from system.scripts.day_skeleton import is_closed  # noqa: E402


LAST_RUN_REL = Path(".beats/nightly-last-run.json")
ARCHIVE_REL = Path("5. Trackers/archive")
PLIST_TEMPLATE_REL = Path("system/config/com.beats.nightly-consolidate.plist.template")
PLIST_NAME = "com.beats.nightly-consolidate.plist"
SKIP_ARCHIVE_DIRS = {"markdown-label-backups"}


def _run_step(name: str, fn) -> dict:
    start = time.perf_counter()
    try:
        detail = fn()
        ok = True
    except Exception as exc:  # noqa: BLE001 - step isolation is the contract.
        detail = f"{type(exc).__name__}: {exc}"
        ok = False
    wall_ms = int((time.perf_counter() - start) * 1000)
    return {"step": name, "ok": ok, "detail": str(detail), "wall_ms": wall_ms}


def _rebuild_context_index(root: Path) -> str:
    index_path = root / "system" / "cache" / "context-router" / "index.json"
    index = context_router.build_index(root, force=True, index_path=index_path)
    return f"indexed {len(index.get('files', []))} files"


def _rebuild_task_master(root: Path) -> str:
    path = task_store.rebuild_task_master(root)
    touched = task_store.normalize_all_status_frontmatter(root)
    return f"rebuilt {path.relative_to(root).as_posix()}; normalized {len(touched)} status value(s)"


def _apply_humanizer(root: Path) -> str:
    result = markdown_humanizer.run_humanizer(root, apply=True)
    return f"scanned {result.scanned} file(s), updated {result.files_updated}"


def archive_hygiene_counts(root: Path) -> dict:
    """Report-only counts. Active tasks already done should be archived;
    archived task notes still open should be reopened or closed properly."""
    active_done = sum(1 for record in task_store.iter_tasks(root) if is_closed(record.status))
    archived_open = 0
    archive_dir = root / ARCHIVE_REL
    if archive_dir.exists():
        for path in sorted(archive_dir.rglob("*.md")):
            if any(part in SKIP_ARCHIVE_DIRS for part in path.parts):
                continue
            if path.name == "INDEX.md":
                continue
            record = task_store.parse_task(path)
            if record is not None and not is_closed(record.status):
                archived_open += 1
    return {"active_done": active_done, "archived_open": archived_open}


def _archive_check(root: Path) -> str:
    counts = archive_hygiene_counts(root)
    return (
        f"{counts['active_done']} active task(s) already done; "
        f"{counts['archived_open']} archived task(s) still open (report-only)"
    )


def _generate_skeleton(root: Path) -> str:
    summary = day_skeleton.generate(root)
    return f"wrote {summary['path']} ({summary['task_count']} active tasks, {len(summary['sections'])} sections)"


def run_nightly(root: Path = ROOT, *, skip_skeleton: bool = False) -> dict:
    steps = [
        _run_step("context-index", lambda: _rebuild_context_index(root)),
        _run_step("task-master", lambda: _rebuild_task_master(root)),
        _run_step("humanizer", lambda: _apply_humanizer(root)),
        _run_step("archive-check", lambda: _archive_check(root)),
    ]
    if skip_skeleton:
        steps.append({"step": "day-skeleton", "ok": True, "detail": "skipped (--skip-skeleton)", "wall_ms": 0})
    else:
        steps.append(_run_step("day-skeleton", lambda: _generate_skeleton(root)))

    summary = {
        "ok": all(step["ok"] for step in steps),
        "ts": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "steps": steps,
    }
    last_run = root / LAST_RUN_REL
    last_run.parent.mkdir(parents=True, exist_ok=True)
    last_run.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def install_launchd(root: Path = ROOT, launch_agents_dir: Path | None = None) -> Path:
    """Render the launchd template to ~/Library/LaunchAgents (user opt-in).

    Prints the ``launchctl load`` command; never executes it.
    """
    template_path = root / PLIST_TEMPLATE_REL
    rendered = template_path.read_text(encoding="utf-8").replace(
        "__REPO_ROOT__", xml_escape(str(root))
    )
    target_dir = launch_agents_dir or (Path.home() / "Library" / "LaunchAgents")
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / PLIST_NAME
    destination.write_text(rendered, encoding="utf-8")
    print(f"Rendered launchd agent to {destination}")
    print("To schedule the 05:30 nightly run, load it yourself:")
    print(f'  launchctl load "{destination}"')
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Nightly consolidation runner.")
    parser.add_argument("--json", action="store_true", help="Print the run summary as JSON.")
    parser.add_argument("--skip-skeleton", action="store_true", help="Skip day-skeleton generation.")
    parser.add_argument(
        "--install-launchd",
        action="store_true",
        help="Render the launchd plist template to ~/Library/LaunchAgents and print the load command.",
    )
    args = parser.parse_args(argv)

    if args.install_launchd:
        install_launchd(ROOT)
        return 0

    summary = run_nightly(ROOT, skip_skeleton=args.skip_skeleton)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for step in summary["steps"]:
            marker = "ok" if step["ok"] else "FAILED"
            print(f"[{marker}] {step['step']}: {step['detail']} ({step['wall_ms']} ms)")
        print(f"Summary written to {LAST_RUN_REL}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
