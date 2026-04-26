---
description: GTM / Launch Strategy. Chains Value Prop Extraction -> Marketing Assets -> Stakeholder Comms.
source_tool: antigravity
source_path: .agents\workflows\archive\launch-gtm.md
imported_at: 2026-04-25T21:29:42.767Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Launch Release Workflow (`/launch`)

This workflow ensures your feature lands with a splash, not a thud.

## Steps

1.  **Extract Value Proposition**
    - **Agent**: `prd-author`
    - **Command**: `/prd "Extract the core Value Prop, Target Audience, and Key Differentiators from [PRD_File]."`
    - **Output**: `2. Products/[Product]/launch/Value_Matrix.md`

2.  **Generate Marketing Assets**
    - **Agent**: `ux-collaborator`
    - **Command**: `/ux "Draft 3 tagline ideas and a 1-paragraph 'Press Release' based on the Value Matrix."`
    - **Input**: `[OUTPUT_MANIFEST].value_matrix` from Step 1
    - **Output**: `2. Products/[Product]/launch/Marketing_Copy.md`

3.  **Draft Release Comms**
    - **Agent**: `stakeholder-manager`
    - **Command**: `/stakeholder "Draft a 'General Availability' email to [Audience]."`
    - **Input**: `[OUTPUT_MANIFEST].marketing_copy` from Step 2
    - **Output**: `2. Products/[Product]/launch/Release_Email.md`

## Usage

```bash
/launch "Feature Name"
```
