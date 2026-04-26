---
description: Export current conversation to archive database
source_tool: antigravity
source_path: .agents\workflows\export.md
imported_at: 2026-04-25T21:29:42.748Z
ai_context_version: 0.9.2
---

# Export Conversation Workflow

## Trigger
User types `/export` or "export this conversation"

## Steps

1. **Create temp markdown file**
   - Use `os.tmpdir()` to get system temp directory
   - Generate filename: `conversation_export_${Date.now()}.md`
   - Write full conversation history to file in markdown format

2. **Call MCP tool**
   - Tool: `export_conversation`
   - Parameters: `{file_path: <absolute_path_to_temp_file>}`
   - **Recommended metadata**: `{conversation_date: 'YYYY-MM-DD', topic: 'Brief summary', project: 'project-name', tags: ['planning', 'bugfix']}`

3. **Confirm to user**
   - On success: "✅ Conversation exported to archive (ID: <conversationId>)"
   - On failure: "❌ Export failed: <error_message>"

## Notes
- Temp file is automatically deleted after successful export
- If export fails, temp file remains for debugging
- User can search archived conversations with `search_archive` MCP tool
