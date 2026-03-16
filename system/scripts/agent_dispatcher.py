"""
Agent Dispatcher — Fan-Out Engine
Antigravity Native Protocol v1.0

Breaks PM tasks into sub-tasks, assigns them to specialized agents,
executes in parallel using ThreadPoolExecutor, and collects results.

Usage:
    from system.scripts.agent_dispatcher import fan_out, classify_task, AGENT_SKILLS

    results = fan_out(
        task={"type": "prd", "context": "Feature request for notifications"},
        agents=["staff-pm", "ux-researcher"]
    )
"""

from __future__ import annotations

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # beats-pm-antigravity-brain/

# ---------------------------------------------------------------------------
# Agent → Skill Capability Map
# Derived from GEMINI.md "Virtual Team" table + agent frontmatter
# ---------------------------------------------------------------------------
AGENT_SKILLS: Dict[str, List[str]] = {
    "cpo": [
        "chief-strategy-officer", "boss-tracker", "vacuum-protocol", "okr-manager"
    ],
    "staff-pm": [
        "task-manager", "boss-tracker", "prd-author", "meeting-synth",
        "delegation-manager", "requirements-translator", "discovery-coach",
        "prioritization-engine", "communication-crafter"
    ],
    "strategist": [
        "chief-strategy-officer", "okr-manager", "competitive-intel",
        "company-profiler", "communication-crafter"
    ],
    "program-manager": [
        "dependency-tracker", "release-manager", "retrospective",
        "task-manager", "risk-guardian"
    ],
    "tech-lead": [
        "engineering-collab", "code-simplifier", "vacuum-protocol",
        "visual-architect"
    ],
    "data-scientist": [
        "data-analytics"
    ],
    "ux-researcher": [
        "ux-researcher", "ux-collaborator", "discovery-coach",
        "visual-processor", "interview-simulator"
    ],
    "gtm-lead": [
        "product-marketer", "competitive-intel", "communication-crafter"
    ],
    "career-coach": [
        "cover-letter-writer", "interview-simulator", "communication-crafter"
    ],
    "frontend-specialist": [
        "frontend-specialist", "frontend-engineer", "visual-architect", "stitch"
    ],
    "talent-scout": [
        "communication-crafter"
    ],
    "resume-architect": [
        "cover-letter-writer", "communication-crafter"
    ],
}

# ---------------------------------------------------------------------------
# Request Classifier
# Maps task keywords → recommended agent roster
# GEMINI.md "REQUEST CLASSIFIER" table, codified.
# ---------------------------------------------------------------------------
CLASSIFIER_ROUTES: List[Tuple[Tuple[str, ...], List[str]]] = [
    (("plan", "roadmap", "vision", "strategy"),        ["cpo", "strategist"]),
    (("track", "task", "jira", "ticket", "triage"),    ["staff-pm"]),
    (("draft", "write", "spec", "prd", "requirement"), ["staff-pm"]),
    (("transcript", "notes", "meeting", "agenda"),     ["staff-pm"]),
    (("data", "metrics", "growth", "funnel", "sql"),   ["data-scientist"]),
    (("user", "interview", "persona", "research"),     ["ux-researcher"]),
    (("launch", "gtm", "marketing", "release"),        ["gtm-lead", "program-manager"]),
    (("dependency", "release plan", "retro", "ship"),  ["program-manager", "staff-pm"]),
    (("discover", "hypothesis", "experiment", "ost"),  ["staff-pm", "ux-researcher"]),
    (("prioritize", "rank", "score", "rice", "kano"),  ["staff-pm"]),
    (("competitive", "battlecard", "market intel"),    ["strategist"]),
    (("communicate", "email", "escalate", "update"),   ["staff-pm"]),
]


def classify_task(task_description: str) -> List[str]:
    """
    Determine which agents should handle a task.
    Legacy: Uses keyword matching (CLASSIFIER_ROUTES).
    Avant-Garde (Vortex Engine): Uses semantic embeddings for high-fidelity routing.

    Args:
        task_description: Free-form task description string.

    Returns:
        List of agent names.
    """
    text = task_description.lower()
    
    # Priority 1: Keyword exact matches (High confidence overrides)
    for keywords, agents in CLASSIFIER_ROUTES:
        if any(kw in text for kw in keywords):
            return agents
            
    # Priority 2: Vortex Semantic Routing (The new baseline)
    try:
        import sys
        # Ensure system/ parent is in path for imports
        if str(SYSTEM_ROOT) not in sys.path:
            sys.path.append(str(SYSTEM_ROOT))
            
        from utils.semantic_router import get_vortex_router
        router = get_vortex_router()
        return router.route_query(task_description)
    except Exception as e:
        # Fallback to Staff PM if router fails
        return ["staff-pm"]


# ---------------------------------------------------------------------------
# Job Result
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    agent: str
    status: str          # "success" | "error" | "skipped"
    output: Any
    duration_ms: float
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ---------------------------------------------------------------------------
# Agent Invocation
# ---------------------------------------------------------------------------

# Registry of callable handlers per agent.
# Each handler receives the task dict and returns an output dict.
_AGENT_HANDLERS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}


def register_handler(agent: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
    """Register a custom invocation handler for an agent."""
    _AGENT_HANDLERS[agent] = handler


def _default_handler(agent: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Default handler: reads the agent's SKILL.md files and returns a
    structured context dict. In full Antigravity runtime this would
    invoke a real LLM call; here it provides the structured prompt context.
    """
    skills = AGENT_SKILLS.get(agent, [])
    agent_file = BRAIN_ROOT / ".agent" / "agents" / f"{agent}.md"
    skill_contents: Dict[str, str] = {}

    # Load agent persona
    agent_persona = ""
    if agent_file.exists():
        agent_persona = agent_file.read_text(encoding="utf-8")

    # Load relevant skill files
    for skill in skills:
        skill_path = BRAIN_ROOT / ".agent" / "skills" / skill / "SKILL.md"
        if skill_path.exists():
            skill_contents[skill] = skill_path.read_text(encoding="utf-8")

    return {
        "agent": agent,
        "task": task,
        "persona_loaded": bool(agent_persona),
        "skills_loaded": list(skill_contents.keys()),
        "context": {
            "agent_persona": agent_persona[:500] if agent_persona else "",
            "skills_summary": {k: v[:300] for k, v in skill_contents.items()},
        },
        "status": "context_loaded",
        "note": "Invoke LLM with this context in Antigravity native runtime.",
    }


def _invoke_agent(agent: str, task: Dict[str, Any]) -> AgentResult:
    """Invoke a single agent and return an AgentResult."""
    start = time.monotonic()
    try:
        handler = _AGENT_HANDLERS.get(agent)
        if handler:
            output = handler(task)
        else:
            output = _default_handler(agent, task)
        duration = (time.monotonic() - start) * 1000
        return AgentResult(agent=agent, status="success", output=output, duration_ms=round(duration, 2))
    except Exception as exc:
        duration = (time.monotonic() - start) * 1000
        return AgentResult(
            agent=agent, status="error", output=None,
            duration_ms=round(duration, 2), error=str(exc)
        )


# ---------------------------------------------------------------------------
# Fan-Out Entry Point
# ---------------------------------------------------------------------------

def fan_out(
    task: Dict[str, Any],
    agents: Optional[List[str]] = None,
    max_workers: Optional[int] = None,
) -> List[AgentResult]:
    """
    Dispatch a PM task to multiple agents in parallel.

    Args:
        task:        Task dict with keys like 'type', 'context', 'priority'.
        agents:      Agent names to invoke. If None, auto-classifies from task context.
        max_workers: Thread pool size. Defaults to len(agents).

    Returns:
        List of AgentResult objects (one per agent, in completion order).
    """
    # Auto-classify if no agents specified
    if not agents:
        context_str = task.get("context", task.get("description", str(task)))
        agents = classify_task(context_str)

    if not agents:
        return []

    workers = max_workers or len(agents)

    results: List[AgentResult] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map: Dict[Future, str] = {
            executor.submit(_invoke_agent, agent, task): agent
            for agent in agents
        }
        for future in as_completed(future_map):
            result = future.result()
            results.append(result)

    # Sort by agent name for deterministic output
    results.sort(key=lambda r: r.agent)
    return results


def fan_out_to_json(
    task: Dict[str, Any],
    agents: Optional[List[str]] = None,
    output_file: Optional[Path] = None,
) -> str:
    """
    Run fan_out and serialize results to JSON.

    Args:
        task:        Task dict.
        agents:      Optional agent list.
        output_file: If provided, write JSON to this path.

    Returns:
        JSON string of results.
    """
    results = fan_out(task, agents)
    payload = [
        {
            "agent": r.agent,
            "status": r.status,
            "duration_ms": r.duration_ms,
            "timestamp": r.timestamp,
            "output": r.output,
            "error": r.error,
        }
        for r in results
    ]
    json_str = json.dumps(payload, indent=2, default=str)

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json_str, encoding="utf-8")

    return json_str


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Fan-out a PM task to multiple agents.")
    parser.add_argument("--task", type=str, required=True, help="Task description or JSON string")
    parser.add_argument("--agents", type=str, nargs="*", help="Agent names (auto-classify if omitted)")
    parser.add_argument("--output", type=Path, help="Write JSON results to this file")
    args = parser.parse_args()

    # Parse task
    try:
        task_dict = json.loads(args.task)
    except json.JSONDecodeError:
        task_dict = {"context": args.task}

    json_output = fan_out_to_json(task_dict, agents=args.agents, output_file=args.output)
    print(json_output)
