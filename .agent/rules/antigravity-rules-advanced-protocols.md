---
source: .agents\rules\assets\advanced-protocols.md
type: antigravity
---

# Advanced Protocols

> Load this file JIT when performing strategic decisions, discovery, or prioritization work.

## 🔋 TOKEN OPTIMIZATION PROTOCOL (v10.0)

### Context Rot Prevention

1. **Research → Plan → Reset → Implement**: Clear context between phases to prevent accumulated noise.
2. **Session Windowing**: Use Antigravity KI system to persist cross-session learnings. Don't re-explain.
3. **Index, Don't Inline**: SKILL.md files should be indexes pointing to `assets/`. Never inline templates.
4. **Priority Loading**: Load P0 skills eagerly, P1/P2 only when triggered.
5. **Single Source of Truth**: `ROUTING.md` for routing. `MANIFEST.json` for registry. No duplicates.

### Skill Archival Protocol

- Skills unused for 30+ days are candidates for archival via `/vacuum`.
- Archived skills move to `.agent/archive/skills/` and are removed from active MANIFEST.json.
- Reactivation: Move back to `.agent/skills/` and update MANIFEST.json.

---

## TIER 2: ADVANCED PROTOCOLS (v7.0)

### 1. Evidence-Based Decision Protocol

Every strategic decision MUST cite one of:

- **Quantitative Data**: Metrics, experiments, dashboards.
- **Qualitative Signal**: User quotes, research insights, verbatim feedback.
- **Expert Judgment**: With explicit assumptions documented in `DECISION_LOG.md`.

> Decisions based on "gut feel" or "I think" without supporting evidence must be flagged and escalated for validation.

### 2. Continuous Discovery Mandate

For features classified as **High Uncertainty** (new market, new user segment, unvalidated problem):

1.  **MUST** use Opportunity Solution Tree (`/discover`) before writing PRD.
2.  **MUST** log top 3 assumptions with evidence grade (Strong/Moderate/Weak/Assumed).
3.  **MUST** define Pivot/Persevere criteria before engineering commitment.
4.  **MUST** run at least one experiment to validate the riskiest assumption.

### 3. Prioritization Discipline

When backlog exceeds 20 items or stakeholders disagree on priority:

1.  **MUST** use a structured framework (`/prioritize`) — default to RICE.
2.  **MUST** document scoring criteria and weights BEFORE scoring items.
3.  **MUST** publish the scored backlog to stakeholders for alignment.
