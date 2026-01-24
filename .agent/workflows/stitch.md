---
description: Interface with the Stitch AI UI/UX design and code generation tool.
---

# /stitch - Design with AI

**Trigger**: User types `/stitch`.

## Steps

1.  **Analyze Intent**: Determine if the user wants to list projects, generate a new design, or enhance a prompt.
2.  **Verify Authentication**: Check if the Stitch MCP server is active and the bearer token/API key is valid.
3.  **Execute Command**:
    - **List Projects**: `gemini stitch projects list` (or use MCP `list_projects`).
    - **Generate Design**: `gemini stitch generate "{{prompt}}"` (or use MCP `generate_screen_from_text`).
    - **Enhance Prompt**: Apply the Stitch Effective Prompting Guide logic.
4.  **Display Results**: Show the generated UI screenshot, code, or project list in the chat.

## Example Prompts

- `/stitch list projects`
- `/stitch create a minimalist yoga app screen`
- `/stitch improve this prompt: [raw prompt]`
