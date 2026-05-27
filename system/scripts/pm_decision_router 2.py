#!/usr/bin/env python3
"""Deterministic preflight router for Beats PM Kit inputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


INTENTS = {
    "task_update",
    "new_task",
    "discovery",
    "scope_challenge",
    "prioritize",
    "create_doc",
    "decision_log",
    "archive_only",
    "ask_user",
}

ROUTING_TARGETS = {
    "task_update": ".agent/workflows/track.md",
    "new_task": ".agent/workflows/track.md",
    "discovery": ".agent/workflows/discover.md",
    "scope_challenge": ".agent/workflows/track.md",
    "prioritize": ".agent/workflows/prioritize.md",
    "create_doc": ".agent/workflows/create.md",
    "decision_log": ".agent/workflows/track.md",
    "archive_only": ".agent/workflows/archive.md",
    "ask_user": ".agent/workflows/chat.md",
}

TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{3,}[a-z]?\b")

SCOPE_TERMS = [
    "scope creep",
    "out of scope",
    "legacy integration",
    "legacy ui",
    "existing ui launch",
    "release management",
    "requirements writer",
    "jira requirements",
    "po-level",
    "po level",
    "day-to-day engineering support",
    "day to day engineering support",
    "tactical eng",
    "tactical engineering",
]

DISCOVERY_TERMS = [
    "discovery",
    "problem space",
    "user research",
    "interview",
    "opportunity",
    "opportunity solution tree",
    "ost",
    "assumption",
    "experiment",
    "validate",
    "validation",
    "desirability",
    "feasibility",
    "viability",
    "hypothesis",
]

PRIORITIZE_TERMS = [
    "prioritize",
    "prioritise",
    "rank",
    "ranking",
    "backlog",
    "rice",
    "ice score",
    "moscow",
    "kano",
    "weighted scoring",
    "cut line",
    "capacity",
]

CREATE_DOC_TERMS = [
    "prd",
    "spec",
    "one-pager",
    "one pager",
    "six-pager",
    "six pager",
    "brief",
    "write up",
    "working backwards",
    "strategy memo",
    "product requirements",
]

DECISION_TERMS = [
    "decision",
    "decided",
    "agreed",
    "aligned",
    "go/no-go",
    "go no-go",
    "tradeoff",
    "trade-off",
    "chosen option",
    "record this",
]

ARCHIVE_TERMS = [
    "fyi",
    "for reference",
    "no action",
    "archive only",
    "save this",
    "parking lot",
]

TASK_UPDATE_TERMS = [
    "blocked",
    "unblocked",
    "done",
    "complete",
    "completed",
    "closed",
    "progress",
    "status",
    "owner",
    "due",
    "deadline",
    "follow up",
    "follow-up",
    "scheduled",
    "waiting",
]

NEW_TASK_TERMS = [
    "todo",
    "to do",
    "action item",
    "follow up",
    "follow-up",
    "need to",
    "needs to",
    "please",
    "should",
    "must",
    "create task",
    "track this",
    "add task",
]


@dataclass
class RouterResult:
    intent: str
    routing_target: str
    confidence: float
    evidence: list[str]
    candidate_updates: list[str]
    blocking_questions: list[str]


def contains_any(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term in text]


def first_sentence(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if not collapsed:
        return ""
    match = re.split(r"(?<=[.!?])\s+", collapsed, maxsplit=1)
    return match[0][:220]


def result(
    intent: str,
    confidence: float,
    evidence: list[str],
    candidate_updates: list[str] | None = None,
    blocking_questions: list[str] | None = None,
) -> RouterResult:
    if intent not in INTENTS:
        raise ValueError(f"Unsupported router intent: {intent}")
    return RouterResult(
        intent=intent,
        routing_target=ROUTING_TARGETS[intent],
        confidence=round(confidence, 2),
        evidence=evidence,
        candidate_updates=candidate_updates or [],
        blocking_questions=blocking_questions or [],
    )


def route_text(text: str) -> RouterResult:
    raw = text or ""
    normalized = raw.lower()
    summary = first_sentence(raw)

    if not normalized.strip():
        return result(
            "ask_user",
            0.1,
            [],
            blocking_questions=["Provide the note, transcript, screenshot text, or task signal to route."],
        )

    task_ids = TASK_ID_RE.findall(raw)
    scope_hits = contains_any(normalized, SCOPE_TERMS)
    if scope_hits:
        return result(
            "scope_challenge",
            0.9,
            [f"scope signal: {hit}" for hit in scope_hits[:3]],
            candidate_updates=[
                "Do not add active work yet; run the task-manager Priority Gate and ask for PM ownership confirmation."
            ],
            blocking_questions=[
                "Is this inside the PM scope defined in `1. Company/ways-of-working.md`?",
                "Who is the accountable owner if this remains outside PM scope?",
            ],
        )

    prioritize_hits = contains_any(normalized, PRIORITIZE_TERMS)
    if prioritize_hits:
        return result(
            "prioritize",
            0.86,
            [f"prioritization signal: {hit}" for hit in prioritize_hits[:3]],
            candidate_updates=["Score or rank the backlog with explicit capacity and cut-line assumptions."],
            blocking_questions=[],
        )

    discovery_hits = contains_any(normalized, DISCOVERY_TERMS)
    if discovery_hits:
        return result(
            "discovery",
            0.84,
            [f"discovery signal: {hit}" for hit in discovery_hits[:3]],
            candidate_updates=[
                "Create or update a discovery brief with outcome, scope boundary, assumptions, experiment, and gate date."
            ],
            blocking_questions=[],
        )

    create_hits = contains_any(normalized, CREATE_DOC_TERMS)
    if create_hits:
        return result(
            "create_doc",
            0.82,
            [f"document signal: {hit}" for hit in create_hits[:3]],
            candidate_updates=["Draft the requested artifact using the matching kit template and source evidence."],
            blocking_questions=[],
        )

    decision_hits = contains_any(normalized, DECISION_TERMS)
    if decision_hits:
        return result(
            "decision_log",
            0.8,
            [f"decision signal: {hit}" for hit in decision_hits[:3]],
            candidate_updates=["Append a decision entry with context, options, choice, rationale, and follow-ups."],
            blocking_questions=[],
        )

    update_hits = contains_any(normalized, TASK_UPDATE_TERMS)
    if task_ids or ("task" in normalized and update_hits):
        evidence = [f"task id: {task_id}" for task_id in sorted(set(task_ids))]
        evidence.extend(f"task update signal: {hit}" for hit in update_hits[:3])
        return result(
            "task_update",
            0.88 if task_ids else 0.72,
            evidence,
            candidate_updates=["Update the matching task detail file before creating any new task."],
            blocking_questions=[] if task_ids else ["Which existing task should receive this update?"],
        )

    archive_hits = contains_any(normalized, ARCHIVE_TERMS)
    action_hits = contains_any(normalized, NEW_TASK_TERMS)
    if archive_hits and not action_hits:
        return result(
            "archive_only",
            0.76,
            [f"archive signal: {hit}" for hit in archive_hits[:3]],
            candidate_updates=["Save compact evidence locally without changing active task state."],
            blocking_questions=[],
        )

    if action_hits:
        return result(
            "new_task",
            0.72,
            [f"action signal: {hit}" for hit in action_hits[:3]],
            candidate_updates=["Run the Priority Gate before adding this as active Task Master work."],
            blocking_questions=[
                "Who owns the outcome?",
                "What due date or decision gate should be attached?",
                "What evidence supports accepting this into active PM scope?",
            ],
        )

    return result(
        "ask_user",
        0.42,
        [summary] if summary else [],
        blocking_questions=[
            "Should this become a task update, discovery brief, decision log, document, prioritization pass, or archive-only note?"
        ],
    )


def read_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", help="Text to classify", default="")
    parser.add_argument("--file", help="File whose text should be classified")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    routed = route_text(read_input(args))
    print(json.dumps(asdict(routed), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
