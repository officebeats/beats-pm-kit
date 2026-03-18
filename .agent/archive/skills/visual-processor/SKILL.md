---
name: visual-processor
description: Extract text and context from images for PM analysis.
triggers:
  - "/paste-image"
  - "/dump"
  - "image analysis"
  - "/screenshot"
version: 2.0.0
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Visual Processor Skill

> **Role**: Extract actionable information from images, screenshots, and visual artifacts for product management workflows.

## Capabilities

### OCR & Text Extraction

- Extract all visible text from images
- Recognize UI labels, buttons, error messages, form fields
- Preserve layout context (e.g., "button next to X")

### Visual Analysis

- Identify UI bugs (misaligned elements, broken layouts)
- Detect error states, empty states, loading states
- Recognize diagrams, flowcharts, wireframes, mockups
- Extract data tables, charts, graphs

### Context Extraction

- Identify application/platform from UI
- Detect user flows and navigation paths
- Spot accessibility issues (color contrast, text size)
- Note design inconsistencies

## Extraction Rules

### For Screenshots

1. **Extract all text** → Process with inbox-processor
2. **Identify UI elements**:
   - Buttons: "[Button: Submit]"
   - Inputs: "[Input: Email field]"
   - Labels: "[Label: User Name]"
3. **Flag bugs**:
   - Broken layouts → "UI bug: Misaligned elements"
   - Missing content → "UI bug: Empty state expected content"
   - Error messages → Extract error text for bug report

### For Diagrams/Specs

1. **Describe diagram type**: Flowchart, Sequence Diagram, Wireframe
2. **Extract labels** → Potential feature names
3. **Identify flows** → Potential user stories
4. **Save as reference** → `0. Incoming/fyi/[Date]_[Topic].md`

### For Tables/Charts

1. **Extract data points** → Save to markdown table
2. **Describe chart type** → Bar chart, Line chart, Pie chart
3. **Extract insights** → Potential metrics/KPIs

## Output Format

``> **Formatting Instructions**: Read the template found at ssets/template_1.md and format your output exactly as shown.``

## Limitations

- Requires text-detectable images
- Handwriting may have accuracy issues
- Complex diagrams may need manual review

## Cross-Skill Routing

- **To `bug-chaser`**: "Here is the screenshot of the crash."
- **To `ux-collab`**: "Here is the competitive analysis screenshot."
- **To `meeting-synth`**: "Here is the whiteboard from the meeting."
- **To `task-manager`**: "Turn this sticky note photo into tasks."
- **To `inbox-processor`**: Process extracted text for task/bug classification
