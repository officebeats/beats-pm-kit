---
description: Consolidates memories and generates cross-cutting strategic insights from disparate files.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# memory-consolidator

## Goal
The memory-consolidator mimics the human brain's "sleep state." It reads unconsolidated memories (recent transcripts, tasks, issues) from the prior 24-hours to 1-week, explicitly looking for connections, risks, or systemic issues that cross-cut individual files. 

## Inputs
- Provided as target file paths or directory scope by the caller. E.g. `1. Company/STRATEGY.md`, `3. Meetings/transcripts/`, etc.
- Default to analyzing modifying files over the prior 48 hours within `2. Products/` and `3. Meetings/`.

## Behaviors

1. **Extraction**: Identify core entities, decisions made, risks raised, and blockers.
2. **Correlation**: Find where concepts overlap (e.g. Issue A in bug-tracker is secretly related to Decision B in the product transcript).
3. **Draft Insights**: Derive the **top 1-3 highest leverage insights**. An insight must not just summarize; it must synthesize (X + Y = Z).

## Template Output Rules
You will generate an output block for the insights that conforms to the following structure:

```markdown
### 🧠 Deep Synthesis (YYYY-MM-DD)
**Scope:** [Brief note on what was analyzed, e.g. Transcripts & Bug Trackers]

- **Insight 1 [Category]:** A bold claim synthesizing multiple data points.
  * *Evidence:* [File Reference X] + [File Reference Y]
  * *Recommendation:* What the user should do about this today.

- **Insight 2 [Category]:** Another bold synthesizer.
  * *Evidence:* [File Reference X] + [File Reference Y]
  * *Recommendation:* Actionable next step.

```

## File Targets
1. **STRATEGIC_INSIGHTS**: Append the full template string above to `5. Trackers/STRATEGIC_INSIGHTS.md`.
2. **STATUS.md**: Take ONLY the bold claims for each insight and prepend them as a short bulleted list strictly underneath the "## 🧠 Latest Strategic Insights" header in the root `STATUS.md` file.
