---
description: Capture product knowledge, competitive intelligence, and strategic context from slides, emails, or verbal notes.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

## Workflow: `/intel` (aliases: `/learn`, `#intel`, `#learn`)

**Agent**: Staff PM → product knowledge capture

---

### Step 1: Detect Input Type

Auto-detect what the user is sharing:

| Input | Detection Signal | Example |
|:------|:----------------|:--------|
| **Slide/Image** | User shares screenshot or image | Allego slides, competitor decks, architecture diagrams |
| **Email paste** | Contains email headers (From, To, Subject, signatures) | Forwarded emails with partner/customer context |
| **Verbal note** | Short conversational text, no structure | "I just learned that..." or "My manager mentioned that..." |
| **Document excerpt** | Longer structured text, headings, bullet points | Confluence pages, PDFs, internal docs |

Do NOT ask the user to classify — detect and proceed.

---

### Step 2: Classify Content Category

Determine where this knowledge belongs:

| Category | Routing Target | Detection Signals |
|:---------|:---------------|:-----------------|
| **Competitive Intel** | `2. Products/competitors/{vendor}.md` | Mentions competitor names, market positioning, win/loss context |
| **Product Architecture** | `2. Products/[product-name].md` or relevant product file | Technical details, API specs, architecture diagrams, data flows |
| **Objection Handling** | `2. Products/[product-name].md` → Objection Handling section | Sales objections, rebuttals, customer concerns |
| **Process / How We Work** | `1. Company/ways-of-working.md` or new process doc | Internal processes, workflows, team norms |
| **Partnership / Customer Intel** | `2. Products/` or `4. People/` | Partner dynamics, customer requirements, contract details |
| **Security / Compliance** | `2. Products/[product]-security.md` | PHI, DEID, LULA, data handling, compliance |
| **Strategic Context** | `2. Products/` or `1. Company/` | Market sizing, roadmap shifts, OKR alignment |

---

### Step 3: Extract & Route

1. **Extract key facts** from the input — structured data points, not summaries.
2. **Check if target file exists**:
   - If exists → Append new intel to relevant section, add source attribution and date.
   - If new → Create file with standard template and initial content.
3. **Tag with source**: Always note where this came from (e.g., "Source: Product Academy, Apr 10").
4. **Cross-reference**: If the intel mentions people, check `4. People/` for profile enrichment.

---

### Step 4: Competitive Intel Log (if applicable)

For competitor/partner profiles, always update the **Intel Log** table:

```markdown
| Date | Source | Intel |
|:-----|:-------|:------|
| 2026-04-10 | Allego Slide | [New fact] |
```

---

### Step 5: Confirm

Show user:
- File(s) updated or created
- Key facts extracted (bullet list)
- Any cross-references made to People or other docs
