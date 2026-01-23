---
name: strategy-synth
description: Synthesize operational signals into strategic insights and themes.
triggers:
  - "/strategy"
  - "/strategy pulse"
  - "/strategy theme"
version: 1.0.0 (Antigravity-First)
author: Beats PM Brain
---

# Strategy Synth Skill

> **Role**: Turn signal into insight. Identify recurring themes, risks, and opportunities.

## 1. Runtime Capability

- **Antigravity**: Parallel fan-out across trackers, meetings, and bugs.
- **CLI**: Sequential reading of sources.

## 2. Native Interface

- **Inputs**: `/strategy`, `/strategy pulse`, `/strategy theme`
- **Context**: `5. Trackers/`, `3. Meetings/`, `2. Products/`
- **Tools**: `view_file`, `write_to_file`

## 3. Cognitive Protocol

1. **Collect**: Sample recent entries from bugs, tasks, and decisions.
2. **Cluster**: Group into 3–5 themes.
3. **Assess**: For each theme, identify impact, confidence, and next action.
4. **Output**: Save to `1. Company/STRATEGY_PULSE.md` or `2. Products/[Product]/STRATEGY_PULSE.md`.

## 4. Output Format

```markdown
# Strategy Pulse — [Date]

## Theme 1: [Name]
- **Signal**: ...
- **Impact**: High/Medium/Low
- **Confidence**: High/Medium/Low
- **Next Action**: ...
```

## 5. Safety Rails

- Always tie insights to source evidence.
