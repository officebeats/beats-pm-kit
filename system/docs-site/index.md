# Beats PM Kit Documentation

Beats PM Kit is a local-first Markdown workspace for turning meetings, transcripts, chats, decisions, and product documents into grounded tasks and delivery artifacts.

## Start Here

- [Getting Started](guide/index.md)
- [Commands Reference](guide/commands.md)
- [Active Skills](skills/index.md)
- [Workflow Catalog](workflows/index.md)
- [Architecture](architecture/index.md)

## Design Principles

- **Registry-backed:** 44 commands are routed through one canonical command registry.
- **Runtime-neutral:** workflows inherit improvements from the user's active supported runtime.
- **Markdown-first:** local notes and tasks remain readable without a dashboard or database.
- **Private by default:** PM source folders are ignored and release checks reject PII, secrets, transcripts, local paths, and runtime state.

Regenerate the catalog without installing dependencies:

```bash
node system/docs-site/scripts/generate-docs.js
```
