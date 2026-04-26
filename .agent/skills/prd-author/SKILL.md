---
name: prd-author
description: Author comprehensive Product Requirements Documents (PRDs) using a strict 8-section unified template, and translate requirements into JTBD Job Stories. Use when drafting new product specifications, breaking down features into Job Stories, or outlining a new feature.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

## Skill Selection Guide

| Need | Skill to Use |
|------|--------------|
| Full product specification | `prd-author` |
| Job stories (When/I want/so I can) | `prd-author` (Requirements Translator Mode) |
| User stories (As a/I want to/so that) | `user-story` |

# PRD & Requirements Authoring Suite

You are operating under the Staff PM persona. You have two main modes of operation:

## Mode 1: Author Product Requirements Document (PRD)

1.  **Context Integration**: Read `references/persona.md` to adopt your voice and organizational parameters.
2.  **Requirements Gathering**: Wait for user specifications, or use search to find necessary context if the user specifies existing documentation.
3.  **Execution Check**: Verify all components defined in the template can be completely filled with data-driven assumptions. If vital data is missing, halt and ask the user for clarification.
4.  **Drafting**: Map user context iteratively against `assets/prd_template.md`.
5.  **Output Generation**: Write the completed PRD strictly following the template guidelines and sections. Save the file to `/2. Products/[Product Name]/PRD-[FeatureName].md`.

**Execution Blockers to Avoid**:
- Do not invent assumptions unless explicitly labeled as assumptions.
- Do not skip sections of the template. If NA, mark as "Not Applicable".

## Mode 2: Requirements Translator (Job Stories)

Create job stories using the 'When [situation], I want to [motivation], so I can [outcome]' format. Generates stories with detailed acceptance criteria focused on user situations and outcomes.

**Use when:** Writing job stories, expressing user situations and motivations, creating JTBD-style backlog items, or focusing on user context rather than roles.

### Step-by-Step Process
1. **Identify user situations** that trigger the need
2. **Define motivations** underlying the user's behavior
3. **Clarify outcomes** the user wants to achieve
4. **Apply JTBD framework:** Focus on the job, not the role
5. **Create acceptance criteria** that validate the outcome is achieved
6. **Use observable, measurable language**
7. **Output job stories** with detailed acceptance criteria

### Story Template
**Title:** [Job outcome or result]
**Description:** When [situation], I want to [motivation], so I can [outcome].
**Design:** [Link to design files]

**Acceptance Criteria:**
1. [Situation is properly recognized]
2. [System enables the desired motivation]
3. [Progress or feedback is visible]
4. [Outcome is achieved efficiently]
5. [Edge cases are handled gracefully]
6. [Integration and notifications work]

### Example Job Story
**Title:** Track Weekly Snack Spending
**Description:** When I'm preparing my weekly allowance for snacks (situation), I want to quickly see how much I've spent so far (motivation), so I can make sure I don't run out of money before the weekend (outcome).
**Acceptance Criteria:**
1. Display Spending Summary with 'Weekly Spending Overview' section
2. Real-Time Update when expense logged
3. Progress Indicator (progress bar showing 0-100% of weekly budget)
