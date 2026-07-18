#!/usr/bin/env python3
"""Plan and rank critical commitment intake for recurring Beats PM commands.

This helper is deterministic and local-first. It does not read or mutate live
third-party systems. It builds named read-only source windows from local manifests and
config, reports expected integration failures loudly, and ranks local work so
leadership/customer commitments do not get buried under ordinary stale work.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts import task_display, task_store  # noqa: E402

CONFIG_TEMPLATE = ROOT / "system" / "config" / "critical_intake.template.json"
CONFIG_LOCAL = ROOT / "system" / "config" / "critical_intake.local.json"
CHAT_MANIFEST = Path("3. Meetings/chat-transcripts/_manifest.json")
TRANSCRIPT_MANIFEST = Path("3. Meetings/transcripts/_manifest.json")
TASK_MASTER = Path("5. Trackers/TASK_MASTER.md")
BOSS_REQUESTS = Path("5. Trackers/critical/boss-requests.md")
SETTINGS = Path("SETTINGS.md")

DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{3,}[a-z]?\b")

READ_ONLY_SOURCES = {
    "slack",
    "outlook",
    "calendar",
    "teams",
    "transcripts",
    "quill",
    "granola",
    "obsidian",
    "agent_memory",
    "atlassian",
}

MUTATION_VERBS = [
    "send",
    "draft",
    "reply",
    "react",
    "schedule",
    "create",
    "assign",
    "transition",
    "comment",
    "upload",
    "patch",
    "delete",
    "move",
]


@dataclass
class SourceHealth:
    source: str
    status: str
    last_successful_at: str
    configured_scope: str
    risk_if_skipped: str
    recommended_fix: str
    requires_user_decision: bool
    read_only: bool = True


@dataclass
class RankedItem:
    title: str
    source: str
    authority_tier: str
    commitment_type: str
    gate_date: str
    evidence_strength: str
    source_refs: list[str]
    completion_state: str
    priority_reason: str
    score: int
    task_id: str = ""
    display_title: str = ""
    started_at: str = ""
    initial_source: str = ""
    latest_source: str = ""
    display_evidence: str = ""
    agent_refs: list[str] | None = None


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(root: Path) -> dict[str, Any]:
    defaults = read_json(root / CONFIG_TEMPLATE.relative_to(ROOT), {})
    local = read_json(root / CONFIG_LOCAL.relative_to(ROOT), {})
    return deep_merge(defaults, local)


def manifest_scopes(root: Path) -> dict[str, list[dict[str, Any]]]:
    manifest = read_json(root / CHAT_MANIFEST, {"scopes": {}})
    grouped: dict[str, list[dict[str, Any]]] = {}
    for key, entry in manifest.get("scopes", {}).items():
        platform = str(entry.get("platform") or key.split(":", 1)[0]).strip().lower()
        grouped.setdefault(platform, []).append(entry)
    return grouped


def newest_success(entries: list[dict[str, Any]]) -> str:
    timestamps = [str(item.get("last_successful_processed_at") or "") for item in entries]
    return max([item for item in timestamps if item], default="")


def scope_summary(entries: list[dict[str, Any]]) -> str:
    scopes = [str(item.get("scope") or item.get("normalized_scope") or "") for item in entries]
    scopes = [scope for scope in scopes if scope]
    if not scopes:
        return ""
    if len(scopes) <= 3:
        return "; ".join(scopes)
    return "; ".join(scopes[:3]) + f"; +{len(scopes) - 3} more"


def _env_path(name: str, *parts: str) -> Path | None:
    base = os.environ.get(name)
    return Path(base, *parts) if base else None


def quill_paths(root: Path) -> list[Path]:
    home = Path.home()
    candidates: list[Path | None] = [
        root / "3. Meetings" / "transcripts" / "quill",
        _env_path("APPDATA", "Quill", "quill.db"),
        _env_path("LOCALAPPDATA", "Quill", "quill.db"),
        home / "Library" / "Application Support" / "Quill" / "quill.db",
    ]
    return [path for path in candidates if path is not None]


def granola_paths(root: Path) -> list[Path]:
    home = Path.home()
    candidates: list[Path | None] = [
        root / "3. Meetings" / "transcripts" / "granola",
        _env_path("APPDATA", "Granola"),
        _env_path("LOCALAPPDATA", "Granola"),
        home / "Library" / "Application Support" / "Granola",
        home / "Library" / "Application Support" / "granola",
    ]
    return [path for path in candidates if path is not None]


def usable_source_path(path: Path) -> bool:
    return path.is_file() or (path.is_dir() and any(item.is_file() for item in path.rglob("*")))


def source_health(root: Path, source: str, source_config: dict[str, Any], grouped_scopes: dict[str, list[dict[str, Any]]]) -> SourceHealth:
    enabled = bool(source_config.get("enabled", True))
    risk = str(source_config.get("risk_if_skipped", "Coverage may be incomplete."))
    read_only = True

    if not enabled:
        return SourceHealth(
            source=source,
            status="disabled",
            last_successful_at="",
            configured_scope="disabled",
            risk_if_skipped=risk,
            recommended_fix="Enable this source in critical_intake.local.json if it should participate in recurring intake.",
            requires_user_decision=False,
            read_only=read_only,
        )

    if source in {"slack", "outlook", "calendar", "teams"}:
        entries = grouped_scopes.get(source, [])
        if entries:
            return SourceHealth(
                source=source,
                status="healthy",
                last_successful_at=newest_success(entries),
                configured_scope=scope_summary(entries),
                risk_if_skipped=risk,
                recommended_fix="Use the manifest-backed named read-only source window for this run.",
                requires_user_decision=False,
                read_only=True,
            )
        return SourceHealth(
            source=source,
            status="missing_scope",
            last_successful_at="",
            configured_scope="",
            risk_if_skipped=risk,
            recommended_fix=f"Add a named read-only {source} source window to critical_intake.local.json or run /beats-comms {source}: <scope> once.",
            requires_user_decision=True,
            read_only=True,
        )

    if source == "transcripts":
        manifest = root / TRANSCRIPT_MANIFEST
        if manifest.exists():
            data = read_json(manifest, {})
            return SourceHealth(
                source=source,
                status="healthy",
                last_successful_at=str(data.get("updated_at") or data.get("last_updated_at") or ""),
                configured_scope="local transcript manifest",
                risk_if_skipped=risk,
                recommended_fix="Process prepared transcript packets before synthesis.",
                requires_user_decision=False,
                read_only=True,
            )
        return SourceHealth(source, "missing_config", "", "", risk, "Run /transcript once or provide a manual transcript packet.", True, True)

    if source == "quill":
        paths = quill_paths(root)
        existing = [path for path in paths if usable_source_path(path)]
        if existing:
            return SourceHealth(source, "healthy", "", str(existing[0]), risk, "Use read-only Quill import or packet fallback.", False, True)
        return SourceHealth(source, "unavailable", "", "; ".join(str(path) for path in paths), risk, "Install/configure Quill export access, paste transcript text, or skip Quill once.", True, True)

    if source == "granola":
        paths = granola_paths(root)
        existing = [path for path in paths if usable_source_path(path)]
        if existing:
            return SourceHealth(source, "healthy", "", str(existing[0]), risk, "Use read-only Granola export or packet fallback.", False, True)
        return SourceHealth(source, "unavailable", "", "; ".join(str(path) for path in paths), risk, "Configure Granola export access, paste transcript text, or skip Granola once.", True, True)

    if source == "obsidian":
        local_config = root / "system" / "config" / "obsidian.local.json"
        mcp_config = root / "system" / "config" / "mcp.obsidian.local.json"
        if local_config.exists() or mcp_config.exists() or (root / ".obsidian").exists():
            return SourceHealth(source, "healthy", "", "local Obsidian config or direct vault", risk, "Use read-only Obsidian search/open context.", False, True)
        return SourceHealth(source, "missing_config", "", "", risk, "Run /obsidian status and configure the kit as a direct vault or MCP read-only source.", True, True)

    if source == "agent_memory":
        if (root / "SESSION_MEMORY.md").exists() or (root / ".agent" / "memory" / "symbolic_graph.mermaid").exists():
            return SourceHealth(source, "healthy", "", "local graph/session memory", risk, "Use read-only graph/session context.", False, True)
        return SourceHealth(source, "degraded", "", "", risk, "Run agent memory setup or use repo-local rg fallback after user approval.", True, True)

    if source == "atlassian":
        artifact_manifest = root / "3. Meetings" / "context-artifacts" / "atlassian" / "_manifest.json"
        if artifact_manifest.exists():
            return SourceHealth(source, "healthy", "", "referenced artifacts manifest", risk, "Use referenced-only local artifacts and read-only fetches.", False, True)
        return SourceHealth(source, "degraded", "", "referenced-only", risk, "Fetch only Jira/Confluence links found in named source evidence, or skip Atlassian once.", True, True)

    return SourceHealth(source, "unavailable", "", "", risk, "Add a supported source health handler.", True, read_only)


def build_health(root: Path) -> list[SourceHealth]:
    config = load_config(root)
    grouped = manifest_scopes(root)
    sources = config.get("default_sources", {})
    return [source_health(root, source, cfg, grouped) for source, cfg in sorted(sources.items())]


def strip_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("~~", "")
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def table_cells(line: str) -> list[str]:
    if not line.strip().startswith("|"):
        return []
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if any(cell.startswith(":---") or cell == "---" for cell in cells):
        return []
    return cells


def extract_task_id(cell: str) -> str:
    match = re.search(r"\[([A-Z][A-Z0-9]+-\d{3,}[a-z]?)\]", cell)
    if match:
        return match.group(1)
    match = TASK_ID_RE.search(cell)
    return match.group(0) if match else ""


def parse_date(text: str) -> dt.date | None:
    match = DATE_RE.search(text or "")
    if not match:
        return None
    try:
        return dt.date.fromisoformat(match.group(1))
    except ValueError:
        return None


def authority_tier(text: str, source: str) -> str:
    lower = f"{source} {text}".lower()
    if any(term in lower for term in ["ceo", "cpo", "cto", "president", "svp", "evp"]):
        return "executive"
    if any(term in lower for term in ["skip-level", "skip level", "boss's boss", "vp "]):
        return "skip_level"
    if any(term in lower for term in ["boss", "direct manager", "manager", "manager"]):
        return "direct_manager"
    if any(term in lower for term in ["director", "leader", "leadership"]):
        return "authorized_leader"
    return "standard"


def commitment_type(text: str, tier: str) -> str:
    lower = text.lower()
    if any(term in lower for term in ["customer", "client", "health plan", "end user", "end-user"]):
        return "external_customer"
    if any(term in lower for term in ["partner", "vendor", "integrator", "implementation partner", "payer", "plan sponsor"]):
        return "partner"
    if any(term in lower for term in ["deadline", "due", "by friday", "by monday", "july", "june"]):
        return "end_user_deadline" if "user" in lower else "internal_deadline"
    if tier != "standard":
        return "leadership"
    return "internal"


def completion_state(text: str) -> str:
    lower = text.lower()
    if "✅" in text or "- [x]" in lower or any(term in lower for term in [" done", "completed", "resolved", "closed"]):
        return "explicit_complete"
    if any(term in lower for term in ["ready for review", "follow-up sent", "handoff complete", "hand-off complete", "draft v1 complete"]):
        return "implied_complete"
    return "open"


def evidence_strength(source: str, text: str) -> str:
    lower = f"{source} {text}".lower()
    if any(term in lower for term in ["slack", "teams", "outlook", "email", "transcript", "calendar", "boss"]):
        return "strong"
    if any(term in lower for term in ["progress", "source", "evidence"]):
        return "moderate"
    return "weak"


def score_item(config: dict[str, Any], tier: str, ctype: str, gate: dt.date | None, state: str) -> tuple[int, str]:
    weights = config.get("ranking", {})
    score = int(weights.get("authority_weights", {}).get(tier, 100))
    score += int(weights.get("commitment_weights", {}).get(ctype, 100))
    reasons = [tier.replace("_", " "), ctype.replace("_", " ")]
    if gate:
        today = dt.date.today()
        days = (gate - today).days
        if days < 0:
            score += 180
            reasons.append("overdue gate")
        elif days <= 2:
            score += 150
            reasons.append("near-term gate")
        elif days <= 7:
            score += 100
            reasons.append("this-week gate")
        elif days <= 14:
            score += 50
            reasons.append("two-week gate")
    if state == "explicit_complete":
        score -= 300
        reasons.append("already complete")
    elif state == "implied_complete":
        score += 40
        reasons.append("completion needs confirmation")
    return score, ", ".join(reasons)


def legacy_task_master_rows(root: Path) -> list[dict[str, str]]:
    """Read pre-v11 Task Master rows without making the old ledger authoritative."""
    items: list[dict[str, str]] = []
    for line in read_text(root / TASK_MASTER).splitlines():
        cells = table_cells(line)
        if len(cells) < 5 or cells[0].lower() in {"id", "task"}:
            continue
        task_id = extract_task_id(cells[0])
        if not task_id:
            continue
        link = re.search(r"\]\(([^)]+\.md)\)", cells[0])
        items.append(
            {
                "task_id": task_id,
                "title": strip_markdown(cells[1]),
                "owner": strip_markdown(cells[2]),
                "due": strip_markdown(cells[3]),
                "status": strip_markdown(cells[4]),
                "source": "Legacy Task Master",
                "path": (Path("5. Trackers") / link.group(1)).as_posix() if link else "",
            }
        )
    return items


def task_rows(root: Path) -> list[dict[str, str]]:
    canonical = [
        {
            "task_id": task.task_id,
            "title": task.title,
            "owner": task.owner,
            "due": task.due,
            "status": task.status,
            "source": "Markdown task note",
            "path": task.path.relative_to(root).as_posix(),
        }
        for task in task_store.iter_tasks(root)
    ]
    known_ids = {item["task_id"] for item in canonical}
    return canonical + [item for item in legacy_task_master_rows(root) if item["task_id"] not in known_ids]


def boss_items(root: Path) -> list[dict[str, str]]:
    text = read_text(root / BOSS_REQUESTS)
    items: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = table_cells(line)
        if len(cells) < 3 or cells[0].lower() in {"id", "date", "task"}:
            continue
        title = strip_markdown(" ".join(cells[:4]))
        if title and not title.startswith(":"):
            items.append({"task_id": extract_task_id(cells[0]), "title": title, "due": " ".join(cells), "status": "boss request", "source": "boss-requests.md"})
    return items


def build_ranked_items(root: Path, mode: str) -> list[RankedItem]:
    config = load_config(root)
    raw_items = task_rows(root) + boss_items(root)
    ranked: list[RankedItem] = []
    for item in raw_items:
        combined = " ".join([item.get("title", ""), item.get("owner", ""), item.get("due", ""), item.get("status", ""), item.get("source", "")])
        tier = authority_tier(combined, item.get("source", ""))
        ctype = commitment_type(combined, tier)
        gate = parse_date(item.get("due", "")) or parse_date(combined)
        state = completion_state(combined)
        score, reason = score_item(config, tier, ctype, gate, state)
        if mode == "boss" and tier != "standard":
            score += 120
            reason += ", boss-mode boost"
        task_id = item.get("task_id", "")
        task_path = root / item["path"] if item.get("path") else None
        if task_id and task_path is not None and task_path.is_file():
            provenance = task_display.build_provenance(task_path, fallback_title=item.get("title", ""), extra_refs=[task_id])
        else:
            provenance = task_display.provenance_from_title(
                item.get("title", ""),
                source=item.get("source", "Local tracker"),
                date=gate.isoformat() if gate else "",
                agent_refs=[task_id] if task_id else [],
            )
        ranked.append(
            RankedItem(
                title=item.get("title", ""),
                source=item.get("source", ""),
                authority_tier=tier,
                commitment_type=ctype,
                gate_date=gate.isoformat() if gate else "",
                evidence_strength=evidence_strength(item.get("source", ""), combined),
                source_refs=[item.get("source", "")],
                completion_state=state,
                priority_reason=reason,
                score=score,
                task_id=task_id,
                display_title=provenance.display_title,
                started_at=provenance.started_at,
                initial_source=task_display.format_source_pointer(provenance.initial_source),
                latest_source=task_display.format_source_pointer(provenance.latest_source),
                display_evidence=task_display.format_evidence(provenance),
                agent_refs=provenance.agent_refs,
            )
        )
    ranked.sort(key=lambda item: (-item.score, item.gate_date or "9999-12-31", item.title))
    return ranked


def build_plan(root: Path, mode: str) -> dict[str, Any]:
    health = build_health(root)
    must_pause = [item for item in health if item.requires_user_decision and item.status != "healthy"]
    source_plan = {
        item.source: {
            "status": item.status,
            "configured_scope": item.configured_scope,
            "last_successful_at": item.last_successful_at,
            "requires_user_decision": item.requires_user_decision,
            "configured_read_window": item.configured_scope,
        }
        for item in health
    }
    return {
        "schema_version": 1,
        "mode": mode,
        "runtime_budget_seconds": int(load_config(root).get("runtime_budget_seconds", 90)),
        "should_pause_for_user": bool(must_pause),
        "read_only_sources": sorted(READ_ONLY_SOURCES),
        "third_party_mutations_require_current_turn_confirmation": MUTATION_VERBS,
        "parallel_groups": [
            ["slack", "outlook", "calendar", "teams"],
            ["transcripts", "quill", "granola"],
            ["obsidian", "agent_memory", "atlassian"],
        ],
        "source_plan": source_plan,
        "user_prompts": [
            {
                "source": item.source,
                "what_failed": item.status,
                "why_it_matters": item.risk_if_skipped,
                "recommended_fix": item.recommended_fix,
            }
            for item in must_pause
        ],
    }


def print_json(data: Any, pretty: bool) -> None:
    print(json.dumps(data, indent=2 if pretty else None, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pretty", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("health", help="Report integration health and prompts.")
    health_parser.add_argument("--json", action="store_true", help="Emit JSON. Default is JSON for automation.")

    plan_parser = subparsers.add_parser("plan", help="Build named read-only source windows.")
    plan_parser.add_argument("--mode", choices=["day", "week", "boss"], required=True)
    plan_parser.add_argument("--json", action="store_true")

    rank_parser = subparsers.add_parser("rank", help="Rank local commitments.")
    rank_parser.add_argument("--mode", choices=["day", "week", "boss"], required=True)
    rank_parser.add_argument("--json", action="store_true")
    rank_parser.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    root = args.root.resolve()

    if args.command == "health":
        health = build_health(root)
        payload = {
            "schema_version": 1,
            "should_pause_for_user": any(item.requires_user_decision and item.status != "healthy" for item in health),
            "sources": [asdict(item) for item in health],
        }
        print_json(payload, args.pretty)
        return 0
    if args.command == "plan":
        print_json(build_plan(root, args.mode), args.pretty)
        return 0
    if args.command == "rank":
        items = build_ranked_items(root, args.mode)[: args.limit]
        print_json({"schema_version": 1, "mode": args.mode, "items": [asdict(item) for item in items]}, args.pretty)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
