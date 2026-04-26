---
description: Run a Socratic deep interview to clarify ambiguous requirements before planning.
source_tool: antigravity
source_path: .agents\workflows\interview.md
imported_at: 2026-04-25T21:29:42.766Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: Native to Antigravity and Claude Code.

# /interview — Socratic Deep Interview Workflow

**Trigger**: `/interview [vague idea]` or when user indicates they don't know exactly what they want or want to ensure you fully understand assumptions.

> **Capability**: Employs mathematical ambiguity gating to ask Socratic questions until the requirement's ambiguity score drops below 20%.

---

## Execution Protocol

### Step 1: Initialization
1. Invoke the `deep-interview` skill.
2. The agent reads the initial problem space and scans the current codebase (`explore` agent) to establish Context.

### Step 2: Interview Loop
1. The agent identifies the weakest dimension of clarity (Goal, Constraint, Success Criteria, Context).
2. The agent asks EXACTLY ONE targeted question aimed at exposing assumptions in that weakest dimension, paying special attention to root-cause analysis (5 Whys), Total Addressable Market constraints, and engineering feasibility.
3. **Ambiguity Gating**: Evaluates ambiguity score mathematically after each answer.
4. If Ambiguity > 0.2 (20%), go back to 2.

### Step 3: Challenge Injection
- **Round 4**: Contrarian mode ("What if the opposite were true?").
- **Round 6**: Simplifier mode ("What's the absolute simplest version?").
- **Round 8**: Ontologist mode ("What IS this, fundamentally?").

### Step 4: Spec Crystallization
When ambiguity Drops below 20%, writes the fully crystallized spec to `.omc/specs/deep-interview-{slug}.md`.

### Step 5: Handoff
Recommend execution via `/build` or `/plan`.
