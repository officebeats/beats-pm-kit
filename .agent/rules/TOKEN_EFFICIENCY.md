---
title: "Token Efficiency & High-Fidelity Processing Standards"
type: "rules"
source: "beats-pm-kit"
---

# ⚡ Token Efficiency & High-Fidelity Processing Standards

> **Objective**: Maximize reasoning depth, fidelity, and processing quality while reducing token consumption by 70%–85% through architectural constraints.

---

## 1. The Bounded 2-Tier Retrieval Protocol
Never dump whole raw transcripts, oversized task ledgers, or entire repositories into the prompt context.

```text
[ User Query / Request ]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│ Tier 1: Compact Index Query (0-50 Tokens)             │
│ • Use vault_query.py, context_router.py, or manifests │
│ • Returns: File path, line numbers, snippet summary   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Tier 2: Surgical Line Selection (50-200 Tokens)       │
│ • Use line selectors: read("path/file.md:140-175")     │
│ • Loads ONLY the exact 20-35 lines of evidence needed │
└────────────────────────────────────────────────────────┘
```

- **Rule**: If a source document exceeds 150 lines, agents **MUST NOT** load the entire file. Query the index or search for line ranges first.

---

## 2. Deterministic Prompt Prefix Caching (90% Cost & Latency Discount)
All supported LLM providers (Anthropic Claude 3.5/3.7, Google Gemini 2.0/1.5, OpenAI GPT-4o) support **Prompt Prefix Caching**.

- **Invariant**: The system prefix (`product_identity`, `safety_boundaries`, `routing_contract`, and core rules) must remain strictly identical across turns.
- **Dynamic Content**: Append dates, user inputs, and tool outputs strictly *after* the stable prefix.
- **Benefit**: Turns a 6,000-token prompt into a 90% cached turn, executing in sub-second latency at 1/10th the cost.

---

## 3. Precomputed Python Heavy Lifting (Zero LLM Tokens)
Never force the LLM to perform mechanical file scanning, date arithmetic, sorting, or table formatting.

- **Morning Briefings (`/day`)**: Run `system/scripts/day_skeleton.py` to compute active tasks, overdue items, and boss asks locally on CPU. Delivers a clean 250-token skeleton with 0 LLM sorting tokens.
- **Task Master Views (`/track`)**: `system/scripts/task_store.py` compiles `TASK_MASTER.md` dynamically from individual task notes.
- **Workstream Rollups (`/week`)**: `system/scripts/workstream_snapshot.py` pre-aggregates active workstream health.

---

## 4. Just-In-Time (JIT) Skill Injection
- Never inject the entire 69-skill catalog into the system prompt.
- The `system/scripts/pm_decision_router.py` classifies user intent in Python ($\approx 2\text{ms}$, 0 tokens) and injects **only the single resolved powerhouse skill**:
  - `product-discovery` for user interviews, OSTs, and assumption mapping.
  - `story-engine` for user stories, epics, WWA, and Gherkin scenarios.
  - `product-strategy` for 7 Powers moats, market sizing, and SaaS economics.
  - `roadmapping` for OKRs, RICE scoring, and horizon roadmaps.
  - `deck-builder` for MBB executive presentations.

---

## 5. Lossless Evidence Compression Standard
Token efficiency must **never** compromise fidelity, evidence, or precision:
- **Preserve Verbatim**: Verbatim customer quotes, financial metrics ($ ARR, % margin), dates, and stakeholder names must never be truncated, abstracted, or summarized away.
- **Eliminate Boilerplate**: Strip repetitive conversational greetings, redundant headings, and empty filler prose.
- **Structured Data Over Long Essays**: Use tables, YAML frontmatter, Mermaid flowcharts, and bulleted checklists instead of verbose narrative paragraphs.
