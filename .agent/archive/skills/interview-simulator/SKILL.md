---
name: interview-simulator
description: Conducting interactive mock interviews with real-time feedback.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Interview Simulator Skill

Use this skill when the user wants to practice for an interview (`/prep` or "mock interview").

## Process

### 1. Context & Setup
Ask the user:
*   **Target Role**: (e.g., Sr. Director of Product)
*   **Target Company**: (e.g., Datavant)

### 2. The Cheat Sheet (Enrichment)
Locate the existing `[Company]_Dossier.md` in `6. Career/Applications/`.
*   **Action**: Append a new section: `# ⚡ Interview Cheat Sheet`.
*   **Content**: Generate 12 Questions (3x4 Categories) with Quick Tips and succinct STAR answers.
*   **Goal**: Consolidate prep into a single "Source of Truth" document.

### 3. The Loop (Interactive)
1.  **Question**: Ask one of the generated questions.
2.  **Listen**: Wait for user response.
3.  **Critique**:
    *   **STAR Check**: Did they use Situation, Task, Action, Result?
    *   **Impact Check**: Did they mention metrics?
    *   **Conciseness**: Was it under 2 minutes?
4.  **Refine**: Suggest a "Gold Standard" version of their answer.

### 4. Debrief
*   Summarize strengths and weaknesses.
*   Assign "Homework" (e.g., "Refine your 'Tell me about yourself' story").
