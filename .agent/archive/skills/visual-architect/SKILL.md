---
name: visual-architect
description: Expert in visualizing concepts through code. Generates Mermaid.js diagrams, ASCII art, and HTML/CSS prototypes.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Visual Architect Skill

Use this skill when the user requests a diagram, flowchart, mockup, or concept visualization.

## capabilities

1.  **Mermaid Diagrams**: Sequence, Flowchart, Gantt, Class, ERD.
    *   **Rule**: Always validate syntax. Use quotes for node labels with special characters.
    *   **Layout**: Prefer Left-Right (LR) for process flows, Top-Down (TD) for hierarchies.

2.  **ASCII Art**: For quick, copy-pasteable text visualizations.
    *   **Rule**: Use monospaced blocks. Keep width under 80 chars.

3.  **HTML Prototypes**: For higher fidelity UI mockups.
    *   **Rule**: Use inline CSS. Use specific aesthetic directives (e.g., "Glassmorphism", "clean typography").

## Instructions

### 1. Identify the Abstraction
What is the core concept? (e.g., "User Flow", "System Architecture", "Timeline").

### 2. Select the Medium
*   **Complex Logic/Flow**: Mermaid Sequence or Flowchart.
*   **Structure/Hierarchy**: Mermaid Class or Graph (TD).
*   **Quick sketch**: ASCII.
*   **UI/UX**: HTML/CSS.

### 3. Generate & Refine
*   Write the code block.
*   **Self-Correction**: If the diagram is too wide, re-orient to TD. If labels are cut off, shorten text.

### 4. Presentation
*   Always wrap in a code block with correct language identifier (`mermaid`, `html`, `text`).
*   Offer to `/export` the visual if it's part of a larger document.
