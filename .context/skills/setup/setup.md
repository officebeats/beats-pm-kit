---
description: Initialize the system and user profile.
source_tool: antigravity
source_path: .agents\workflows\archive\setup.md
imported_at: 2026-04-25T21:29:42.806Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /setup - First Time User Experience

**Trigger**: User types `/setup`.

## Steps

1. **Execute**: Run the interactive setup wizard.
   - Command: `python system/scripts/setup.py`
2. **Verify**: Ensure `SETTINGS.md` was created.
