---
description: Trigger deep memory consolidation over recent files to surface cross-cutting strategic insights.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# 🧠 /reflect — Memory Consolidation Workflow

This workflow mimics the "sleep state" of a human brain by cross-referencing disparate files created over the last 24-48 hours to find non-obvious correlations, hidden risks, and strategic alignments.

## Prerequisites
- Load `memory-consolidator` skill from `.agent/skills/memory-consolidator/SKILL.md`
- Activate **Chief Product Officer** or **Product Strategist** agent

## Steps

1. **Task Boundary (Deep State)**:
    - **Control**: Call `task_boundary(Mode="PLANNING", TaskName="Memory Consolidation Phase")`.
    - **Goal**: Enter the analytical state required for deep synthesis.

2. **Retrieve Unconsolidated Memories**:
    - Run the helper python script to find recently modified files:
      `python .agent/skills/memory-consolidator/scripts/consolidate.py --hours 48`
    - Read the `FILE_TARGET` paths output by the script using parallel `view_file` calls.

3. **Synthesize & Correlate**:
    - **Action**: Use the `memory-consolidator` rules. Do NOT just summarize the files one-by-one. You must find where *File A* intersects with *File B*.
    - **Identify**: What did we decide in a meeting that contradicts a PRD? What bug is actually a symptom of a larger system problem?

4. **Output to Ledger**:
    - Append the full analytical block to `5. Trackers/STRATEGIC_INSIGHTS.md`. (Create the file if it does not exist, adding a `# Strategic Insights Ledger` header).

5. **Update Dashboard**:
    - Prepend **only the bold insight claims** as bullet points under the `## 🧠 Latest Strategic Insights` header inside the root `STATUS.md` file. Provide a brief 1-sentence synopsis for the week.

6. **Notify**:
    - Inform the user that the Sleep State analysis is complete and flag any critical Red/Amber warnings immediately.
