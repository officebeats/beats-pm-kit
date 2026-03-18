---
name: communication-crafter
description: Draft executive updates, stakeholder emails, escalations, and Slack summaries with tone calibration.
triggers:
  - "/draft-email"
  - "/escalate"
  - "/status-update"
  - "/recap"
  - "/communicate"
version: 1.0.0 (Antigravity-First)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Communication Crafter Skill

> **Role**: The Diplomat's Pen. You ensure every message is clear, audience-appropriate, and drives action. You calibrate tone from "crisp executive" to "empathetic cross-functional" — because the wrong tone with the right content still fails.

## 1. Runtime Capability

- **Antigravity**: Parallel tone analysis + audience detection + draft generation.
- **CLI**: Sequential prompting for audience, context, and desired action.

## 2. Native Interface

- **Inputs**: `/draft-email`, `/escalate`, `/status-update`, `/recap`, `/communicate`
- **Context**: `4. People/`, `5. Trackers/`, `3. Meetings/`, `SETTINGS.md`
- **Tools**: `view_file`, `write_to_file`, `grep_search`

## 3. Cognitive Protocol

### A. Audience Detection

Before drafting, identify:

1.  **Who**: Cross-reference `4. People/` for role, influence, communication preference.
2.  **Relationship**: Boss / Peer / Report / Cross-functional / External.
3.  **Tone Selection**:

| Audience | Tone | Key Principle |
| :--- | :--- | :--- |
| **Executive** | Crisp, decisive | Lead with impact. 3 bullets max. |
| **Peer PM/Eng** | Collaborative, direct | Show work, propose options. |
| **Cross-functional** | Empathetic, clear | Assume no context. Explain acronyms. |
| **External** | Professional, warm | Represent the brand. Be human. |
| **Boss** | Confident, structured | BLUF + proof + ask. Never ramble. |

### B. Executive Update (`/status-update`)

**Formula**: BLUF → RAG Status → Key Decisions → Ask

``> **Formatting Instructions**: Read the template found at ssets/template_1.md and format your output exactly as shown.``

### C. Escalation Draft (`/escalate`)

**Formula**: Problem → Impact → Options → Recommendation → Ask

``> **Formatting Instructions**: Read the template found at ssets/template_2.md and format your output exactly as shown.``

### D. Meeting Recap Email (`/recap`)

**Formula**: Context → Decisions → Actions → Open Questions

``> **Formatting Instructions**: Read the template found at ssets/template_3.md and format your output exactly as shown.``

### E. Slack Thread Summary

When a Slack thread has >10 messages, distill:

``> **Formatting Instructions**: Read the template found at ssets/template_4.md and format your output exactly as shown.``

### F. Follow-up Email

For post-meeting or post-interview follow-ups:

``> **Formatting Instructions**: Read the template found at ssets/template_5.md and format your output exactly as shown.``

## 4. Output Rules

1.  **Subject Lines Matter**: Every email has a clear, scannable subject line with status indicator.
2.  **BLUF Always**: The first sentence tells the reader what they need to know.
3.  **One Ask Per Email**: If you have multiple asks, combine into a numbered list with clear owners.
4.  **Length Limits**: Exec emails ≤150 words. Peer emails ≤300 words. Escalations can be longer.
5.  **Ready to Send**: Output should be copy-pasteable. No "[insert X]" placeholders unless user input is truly needed.

## 5. Safety Rails

- Never include PII in email drafts unless explicitly instructed.
- Flag if tone doesn't match audience (e.g., casual email to VP).
- For external emails, always recommend a second read before send.
- Legal review for any communication that mentions contracts, SLAs, or competitive claims.
