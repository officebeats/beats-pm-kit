---
name: agentic-memory
description: Local-first dual-pillar agentic memory inspired by TencentDB-Agent-Memory.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# agentic-memory

## Goal
The `agentic-memory` skill provides a dual-pillar local-first memory system (Symbolic Short-Term Memory and Layered Long-Term Memory). It helps reduce in-context token bloat by offloading verbose traces, replacing them with a high-density Mermaid graph, and maintaining clean atomic facts and scenario blocks.

## Pillar 1: Symbolic Short-Term Memory

1. **Log Offloading (L0 Traces)**:
   - When raw terminal outputs, API schemas, large database dumps, or intermediate reasoning steps are extremely verbose and would clutter subsequent context, offload them to an L0 trace file:
     `python system/scripts/agentic_memory.py log-trace "<source>" "<raw-log-content>"`
   - Cite the created trace file instead of including the raw data in your response.

2. **Mermaid Graph State**:
   - The graph represents the active entities (tasks, files, milestones) and their relationships.
   - Maintain the graph by programmatically adding or removing nodes and edges:
     `python system/scripts/agentic_memory.py update-graph --add-node "<ID>" "<LABEL>" --add-edge "<SRC>" "<DST>" "<LABEL>"`
   - When a node is completed or no longer relevant, remove it:
     `python system/scripts/agentic_memory.py update-graph --remove-node "<ID>"`

## Pillar 2: Layered Long-Term Memory

1. **L1 Atomic Facts**:
   - Save clean, deduplicated, standalone facts (e.g. user OS preferences, configuration limits, directory layouts) that should persist across sessions:
     `python system/scripts/agentic_memory.py add-fact "<fact-content>" --category "<category>"`
   - Check existing facts with `python system/scripts/agentic_memory.py list-facts` before adding new ones.

2. **L2 Scenarios**:
   - Log structured scenario blocks when completing complex workflows, sprint planning, or a system health check:
     `python system/scripts/agentic_memory.py add-scenario "<title>" "<description>" --details "<details>"`

3. **L3 Persona**:
   - Rely on `1. Company/ways-of-working.md`, `SETTINGS.md`, and `4. People/PEOPLE.md` as the L3 persona.

## System Integration
- The memory system automatically synchronizes with `SESSION_MEMORY.md` in the workspace root whenever changes are made.
- Read `SESSION_MEMORY.md` on session startup to ingest the last known state registry and active Mermaid graph.
