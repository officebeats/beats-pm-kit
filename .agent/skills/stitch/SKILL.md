---
name: stitch
description: Official interface for the Stitch AI UI/UX design tool via MCP.
triggers:
  - "/stitch"
  - "/design"
version: 1.0.0
author: Beats PM Brain (Official Stitch Integration)
---

# Stitch AI Official Interface

> **Role**: Interface for the Google Cloud Stitch service.

## 1. Authentication Lifecycle

This integration uses a **Persistent API Key** from the Google Cloud Console.

- **Status**: Hooked Up (Permanent)
- **Key Location**: Managed in `.gemini/settings.json` and Claude Desktop.
- **Refresh**: No manual refresh is required.

## 2. Capabilities & Tools

Once authenticated, you have access to:

- `create_project`: Start a new UI project.
- `generate_screen_from_text`: Design UIs with natural language.
- `list_projects`: View all your Stitch designs.
- `get_screen`: Retrieve HTML/Tailwind code.

## 3. Example Use Cases

- "List my Stitch projects."
- "Create a new project called 'Fitness Tracker'."
- "Generate a minimalist dashboard screen for the Fitness Tracker project."
- "Add a dark mode toggle to the current screen."

## 4. Troubleshooting & Verification

- **Token/Key Errors**: If persistent keys fail with a 401/403, verify GCP project status.
- **Model Capacity (429)**: If the model is exhausted, **Invoke Browser Subagent** to check the Stitch dashboard (`https://stitch.withgoogle.com/`) for manual status or alternative generation tools.
- **Grant Permissions**: Ensure `stitch.googleapis.com` is enabled on your project `gen-lang-client-0123237693`.
