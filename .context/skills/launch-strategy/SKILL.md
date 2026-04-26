---
name: launch-strategy
description: Multi-agent system for product launch intelligence and strategy, analyzing markets and competitors.
source_tool: antigravity
source_path: .agents\skills\launch-strategy\SKILL.md
imported_at: 2026-04-25T21:29:42.768Z
ai_context_version: 0.9.2
---

# Product Launch Intelligence Agent

**Multi-agent system for product launch intelligence and strategy, analyzing markets and competitors.**

This skill leverages an advanced Python-based AI Agent or Multi-Agent Team located in the `scripts/` directory.

## Instructions
1. Use this skill whenever the user triggers the associated playbook or asks for launch-strategy.
2. Navigate to `scripts/` inside this skill's directory.
3. Review the `requirements.txt` and python script to understand how to invoke the agent (e.g. via `streamlit run` or `python`).
4. Execute the agent script to perform the requested tasks.

## Protocol constraints
- Do not hallucinate capabilities. Rely on the underlying python agent.
- Keep output concise and delegate complex reasoning to the agent in `scripts/`.
