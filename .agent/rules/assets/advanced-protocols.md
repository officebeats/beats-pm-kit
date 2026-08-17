# Advanced Protocols

> Load this file JIT when performing strategic decisions, discovery, or prioritization work.

## 🔋 TOKEN OPTIMIZATION PROTOCOL (v10.0)

### Context Rot Prevention

1. **Research → Plan → Reset → Implement**: Clear context between phases to prevent accumulated noise.
2. **Session Windowing**: Use Antigravity KI system to persist cross-session learnings. Don't re-explain.
3. **Index, Don't Inline**: SKILL.md files should be indexes pointing to `assets/`. Never inline templates.
4. **Priority Loading**: Load P0 skills eagerly, P1/P2 only when triggered.
5. **Single Source of Truth**: `.agent/command-registry.json` owns routing. `ROUTING.md` and `MANIFEST.json` are generated views.

### SKILL.md Quick Path Convention

Large skills must open with a distilled fast lane so routine runs avoid loading the full body.

- Any `SKILL.md` whose size excluding the Quick Path section exceeds 5500 bytes MUST carry a `## Quick Path` section.
- Place it as the **first H2** in the body — immediately after the title (and any intro prose), before every other section.
- Content budget: **<= 1200 characters** (~300 tokens). A numbered 3–7 step happy path plus one line stating when to read deeper sections.
- Distill strictly from the skill's own body. Never introduce capabilities, paths, or commands the body does not already define.
- Check compliance with `python3 -m system.scripts.skill_lint --report` (advisory) or `--strict` (exit 1 on violations).

### Skill Removal Protocol

- Unused skills are reviewed with regression evidence before deletion.
- Do not maintain a dormant tracked archive that expands search and context surfaces.
- Restore intentionally removed skills from version control history when evidence supports reintroduction.

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
