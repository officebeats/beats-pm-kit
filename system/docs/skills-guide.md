# External Skills Integration Guide

The Antigravity Kit is designed to be compatible with the **Agent Skills** open standard. This allows you to easily import skills from external libraries like [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills).

## How to Add a Skill Manually

1.  **Identify the Skill**: Browse the `skills/` directory in the `stitch-skills` repository.
2.  **Create Directory**: Create a new folder in `.agent/skills/[skill-name]/`.
3.  **Copy SKILL.md**: Download the `SKILL.md` from the source repo and place it in the new folder.
4.  **Verify Triggers**: Open the `SKILL.md` and check the `triggers:` field in the YAML frontmatter. These are the commands you can use in chat.
5.  **Test**: Ask Antigravity or your preferred CLI tool to run one of the triggers.

## Available External Skills

| Skill              | Category      | Trigger   | Description                                     |
| :----------------- | :------------ | :-------- | :---------------------------------------------- |
| `design-md`        | Documentation | `/design` | Generates a `DESIGN.md` for your UI components. |
| `react-components` | Frontend      | `/react`  | Converts Stitch screens to React components.    |

## Why use external skills?

- **Standardization**: Skills follow a few-shot learning pattern that works across Gemini CLI, Claude Code, and Antigravity.
- **Portability**: You can share skills between different AI-powered projects.
- **Community-Powered**: Tap into a growing library of specialized PM and Engineering expertise.
