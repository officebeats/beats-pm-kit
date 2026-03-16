"""
Result Synthesizer — Fan-Out Output Aggregator
Antigravity Native Protocol v1.0

Merges outputs from multiple parallel agent invocations into a
single coherent PM artifact. Handles conflict detection and
produces structured Markdown summaries.

Usage:
    from system.scripts.result_synthesizer import synthesize, merge_to_markdown

    results = fan_out(task, agents)
    summary = merge_to_markdown(task, results)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # beats-pm-antigravity-brain/


@dataclass
class SynthesisReport:
    task: Dict[str, Any]
    agent_count: int
    successful: int
    failed: int
    total_duration_ms: float
    conflicts: List[str]
    merged_output: Dict[str, Any]
    markdown_summary: str
    timestamp: str


def synthesize(
    task: Dict[str, Any],
    results: List[Any],        # List[AgentResult] — typed loosely to avoid circular import
) -> SynthesisReport:
    """
    Aggregate fan-out results into a unified synthesis report.

    Merge strategy:
    - Skills: union of all unique skills loaded
    - Outputs: keyed by agent name
    - Conflicts: detected when two agents produce different values
      for the same key in their output dicts

    Args:
        task:    Original task dict.
        results: List of AgentResult objects from fan_out().

    Returns:
        SynthesisReport with merged output and Markdown summary.
    """
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "error"]
    total_ms = sum(r.duration_ms for r in results)

    # Merge outputs: collect all data keyed by agent
    merged: Dict[str, Any] = {"agents": {}}
    all_skills: List[str] = []
    conflicts: List[str] = []

    for result in successful:
        agent = result.agent
        output = result.output or {}
        merged["agents"][agent] = output

        # Accumulate loaded skills
        skills_loaded = output.get("skills_loaded", [])
        all_skills.extend(s for s in skills_loaded if s not in all_skills)

    merged["skills_activated"] = sorted(set(all_skills))
    merged["task_type"] = task.get("type", "unknown")

    # Detect conflicts: same key, different values across agent outputs
    key_values: Dict[str, Dict[str, Any]] = {}
    for agent, output in merged["agents"].items():
        for key, val in output.items():
            if key in ("agent", "task", "context", "persona_loaded",
                       "skills_loaded", "skills_summary", "note", "status"):
                continue
            if key not in key_values:
                key_values[key] = {}
            key_values[key][agent] = val

    for key, agents_map in key_values.items():
        unique_vals = set(str(v) for v in agents_map.values())
        if len(unique_vals) > 1:
            conflicts.append(
                f"Key '{key}' has conflicting values: "
                + ", ".join(f"{a}={v}" for a, v in agents_map.items())
            )

    markdown = _render_markdown(task, results, merged, conflicts, total_ms)

    return SynthesisReport(
        task=task,
        agent_count=len(results),
        successful=len(successful),
        failed=len(failed),
        total_duration_ms=round(total_ms, 2),
        conflicts=conflicts,
        merged_output=merged,
        markdown_summary=markdown,
        timestamp=datetime.utcnow().isoformat(),
    )


def _render_markdown(
    task: Dict[str, Any],
    results: List[Any],
    merged: Dict[str, Any],
    conflicts: List[str],
    total_ms: float,
) -> str:
    """Render a Markdown summary of the fan-out results."""
    lines: List[str] = []
    task_type = task.get("type", "Task")
    task_ctx = task.get("context", task.get("description", ""))

    lines.append(f"# 🤖 Agent Fan-Out Report — {task_type.upper()}")
    lines.append(f"\n> **Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ")
    lines.append(f"> **Agents**: {len(results)}  |  **Duration**: {total_ms:.0f}ms\n")

    if task_ctx:
        lines.append(f"**Task Context**: {task_ctx}\n")

    # Agent results table
    lines.append("## Agent Results\n")
    lines.append("| Agent | Status | Skills Loaded | Duration |")
    lines.append("|-------|--------|---------------|----------|")
    for r in sorted(results, key=lambda x: x.agent):
        icon = "✅" if r.status == "success" else "❌"
        output = r.output or {}
        skills = ", ".join(output.get("skills_loaded", [])) or "—"
        lines.append(f"| **{r.agent}** | {icon} {r.status} | {skills} | {r.duration_ms:.0f}ms |")

    # Skills activated
    skills = merged.get("skills_activated", [])
    if skills:
        lines.append(f"\n## Skills Activated ({len(skills)})\n")
        for skill in skills:
            lines.append(f"- `{skill}`")

    # Conflicts
    if conflicts:
        lines.append("\n## ⚠️ Conflicts Detected\n")
        for conflict in conflicts:
            lines.append(f"- {conflict}")
    else:
        lines.append("\n> ✅ No conflicts detected across agent outputs.\n")

    # Failed agents
    failed = [r for r in results if r.status == "error"]
    if failed:
        lines.append("\n## ❌ Failed Agents\n")
        for r in failed:
            lines.append(f"- **{r.agent}**: {r.error}")

    # Next steps
    lines.append("\n## 🚀 Next Steps\n")
    lines.append(
        "Review agent outputs and apply to the appropriate trackers or documents. "
        "Use `/vacuum` if tracker writes created duplicates."
    )

    return "\n".join(lines)


def merge_to_markdown(
    task: Dict[str, Any],
    results: List[Any],
    output_file: Optional[Path] = None,
) -> str:
    """
    Convenience wrapper: synthesize + return (and optionally save) Markdown.

    Args:
        task:        Original task dict.
        results:     List of AgentResult from fan_out().
        output_file: Optional path to write the Markdown report.

    Returns:
        Markdown string.
    """
    report = synthesize(task, results)
    md = report.markdown_summary

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md, encoding="utf-8")

    return md


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Synthesize fan-out results from a JSON file.")
    parser.add_argument("results_file", type=Path, help="JSON file containing AgentResult list")
    parser.add_argument("--task", type=str, default="{}", help="Task JSON string")
    parser.add_argument("--output", type=Path, help="Write Markdown report to this file")
    args = parser.parse_args()

    if not args.results_file.exists():
        print(f"Error: {args.results_file} not found.", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(args.results_file.read_text(encoding="utf-8"))

    # Reconstruct lightweight result objects
    from types import SimpleNamespace
    result_objs = [SimpleNamespace(**r) for r in raw]

    task_dict = json.loads(args.task)
    md = merge_to_markdown(task_dict, result_objs, output_file=args.output)
    print(md)
