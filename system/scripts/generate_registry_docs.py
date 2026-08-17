#!/usr/bin/env python3
"""Generate routing, manifest, architecture, and compatibility docs from registry v3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts.feature_inventory import collect_inventory
from system.scripts.harness_registry import render_lite_registry
from system.utils.command_registry import (
    PROFILE_NAMES,
    build_command_catalog,
    get_execution_profiles,
    get_harness_policy,
    get_runtime_policy,
    load_command_registry,
)


def _version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def render_manifest(root: Path) -> str:
    inventory = collect_inventory(root)
    registry = load_command_registry(root)
    profiles = get_execution_profiles(root)
    manifest: dict[str, Any] = {
        "schema_version": 3,
        "name": "beats-pm-kit",
        "version": _version(root),
        "description": "Generated index of canonical agents, skills, workflows, runtimes, and execution profiles.",
        "generated_by": "system/scripts/generate_registry_docs.py",
        "routing_source": ".agent/command-registry.json",
        "harness": get_harness_policy(root),
        "agents": {
            "count": inventory["agents"]["count"],
            "directory": ".agent/agents/",
            "names": inventory["agents"]["names"],
        },
        "skills": {
            "count": inventory["skills"]["count"],
            "directory": ".agent/skills/",
            "names": inventory["skills"]["names"],
        },
        "workflows": {
            "count": inventory["workflows"]["count"],
            "directory": ".agent/workflows/",
            "commands": [f"/{name}" for name in inventory["workflows"]["names"]],
            "protected": True,
        },
        "runtimes": {
            "selection": registry["runtime_policy"]["selection"],
            "supported": registry["runtime_policy"]["supported"],
            "default_model": registry["runtime_policy"]["default_model"],
        },
        "execution_profiles": {
            name: {
                **profiles[name],
                "commands": registry["command_profiles"][name],
            }
            for name in PROFILE_NAMES
        },
    }
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def render_routing(root: Path) -> str:
    catalog = build_command_catalog(root)
    visible = [item for item in catalog if item["visibility"] != "hidden"]
    hidden = [item for item in catalog if item["visibility"] == "hidden"]
    rows = [
        "# Beats PM Kit Routing",
        "",
        "> Generated from `.agent/command-registry.json` by `system/scripts/generate_registry_docs.py`.",
        "> Edit the registry, never this file.",
        "",
        "The registry is the only routing source of truth. Runtime adapters and this human-readable table are derived views.",
        "",
        "| Command | Profile | Aliases | Runtime adapter |",
        "| --- | --- | --- | --- |",
    ]
    for item in visible:
        aliases = ", ".join(f"`/{alias}`" for alias in item["aliases"]) or "—"
        adapter = (
            f"Skill `{item['codex_skill_name']}`"
            if item["codex_promotion"] == "skill"
            else "Dispatch only"
        )
        rows.append(
            f"| `/{item['name']}` | {str(item['execution_profile']).title()} | {aliases} | {adapter} |"
        )
    rows.extend(
        [
            "",
            "## Escalation",
            "",
            "Conflicting evidence, high-stakes decisions, external mutations, broad changes, and failed validation escalate to Deep. Runtime model defaults remain inherited; explicit promotions stay local and evidence-gated.",
            "",
        ]
    )
    if hidden:
        rows.extend(
            [
                "## Hidden / Legacy Commands",
                "",
                "Decluttered from the discovery table above because they are dispatch-only utilities superseded by the Diamond 6 workflow. They are not deleted: each workflow file still exists under `.agent/workflows/` and resolves normally when a user types the exact command.",
                "",
                ", ".join(f"`/{item['name']}`" for item in hidden),
                "",
            ]
        )
    return "\n".join(rows)


def render_architecture(root: Path) -> str:
    inventory = collect_inventory(root)
    profiles = get_execution_profiles(root)
    harness = get_harness_policy(root)
    return f"""# Beats PM Kit Architecture

> Generated from `.agent/command-registry.json` and the canonical `.agent/` tree.

## Current Surface

| Surface | Count | Canonical location |
| --- | ---: | --- |
| Agents | {inventory['agents']['count']} | `.agent/agents/` |
| Skills | {inventory['skills']['count']} | `.agent/skills/` |
| Workflows | {inventory['workflows']['count']} | `.agent/workflows/` |
| Runtime adapters | {inventory['runtimes']['count']} | Generated from the registry |

## Source Boundaries

- `.agent/command-registry.json` owns the schema-v3 harness contract, routing, aliases, execution profiles, escalation signals, and runtime policy.
- `.agent/workflows/` owns workflow behavior.
- `.agent/skills/` owns reusable PM methods.
- `MANIFEST.json`, `command-registry.lite.json`, `rules/ROUTING.md`, `CODEX_COMMANDS.md`, runtime adapters, and compatibility documentation are generated views.
- `.beats/model-policy.json` is ignored local state for explicit, evaluated model promotions.

## Execution Profiles

| Profile | Intent | Default model |
| --- | --- | --- |
| Fast | {profiles['fast']['purpose']} | `inherit` |
| Balanced | {profiles['balanced']['purpose']} | `inherit` |
| Deep | {profiles['deep']['purpose']} | `inherit` |

## Loading Flow

```text
User request
  -> command registry
  -> one workflow and execution profile
  -> at most {harness['routing']['maximum_initial_sources']} directly relevant sources
  -> active runtime capability probe
  -> inherited model or explicit local promotion
  -> validation and durable Markdown output
```

Unknown capabilities are denied. The kit does not silently switch providers, rewrite skills, or persist model output outside ignored local evaluation storage.

## Harness Contract

- Product name: **{harness['name']}**
- Primary runtimes: Antigravity, Codex, and Claude
- Compatibility runtimes: Gemini CLI and KiloCode
- Response profiles: `compact_operator`, `artifact`, and `verbatim`
- Context checkpoint: completed phase boundary at {harness['checkpoint_policy']['context_threshold_percent']}% context, or before the next phase will not fit; checkpoints append `## Checkpoint <ISO8601>` anchors and never rewrite earlier anchors
- Evidence rule: compacted context remains addressable; raw evidence is authoritative
- Optimizer rule: one change per held-out trial and human approval before promotion
"""


def render_runtime_compatibility(root: Path) -> str:
    policy = get_runtime_policy(root)
    adapters = policy.get("adapters", {})
    rows = [
        "# Runtime and Model Compatibility",
        "",
        "> Generated from `.agent/command-registry.json`. Edit the registry, not this table.",
        "",
        "| Runtime | Adapter entrypoint | Profiles | Default model | Explicit promotion |",
        "| --- | --- | --- | --- | --- |",
    ]
    for runtime in policy["supported"]:
        rows.append(
            f"| {runtime.title()} | `{adapters[runtime]}` | Fast, Balanced, Deep | `inherit` | `.beats/model-policy.json` |"
        )
    rows.extend(
        [
            "",
            "Active-runtime probes determine capabilities and versions. An unavailable or ambiguous runtime fails closed. Missing Deep support retains the active runtime's inherited model and emits a downgrade warning; it never causes a silent provider switch.",
            "",
        ]
    )
    return "\n".join(rows)


def generated_files(root: Path = ROOT) -> dict[Path, str]:
    return {
        root / ".agent" / "MANIFEST.json": render_manifest(root),
        root / ".agent" / "rules" / "ROUTING.md": render_routing(root),
        root / ".agent" / "ARCHITECTURE.md": render_architecture(root),
        root / "system" / "docs" / "runtime-compatibility.md": render_runtime_compatibility(root),
        root / ".agent" / "command-registry.lite.json": render_lite_registry(root),
    }


def write_generated_files(root: Path = ROOT) -> list[str]:
    changed: list[str] = []
    for path, content in generated_files(root).items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        changed.append(path.relative_to(root).as_posix())
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    drift = [
        path.relative_to(root).as_posix()
        for path, content in generated_files(root).items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    if args.check:
        if drift:
            print("Registry-derived files are stale:", file=sys.stderr)
            for path in drift:
                print(f"- {path}", file=sys.stderr)
            return 1
        print("Registry-derived files are current.")
        return 0
    changed = write_generated_files(root)
    print(f"Generated {len(generated_files(root))} registry-derived files; changed {len(changed)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
