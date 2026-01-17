# Contributing to Beats PM Antigravity Brain

## Philosophy

This project uses the **Gemini CLI Skills Protocol**. Agents are small, specialized, and loosely coupled. We prioritize:

1. **Speed**: Agents must be fast. `waitForPreviousTools: false` is preferred.
2. **Simplicity**: Markdown files > databases.
3. **Privacy**: User data never leaves `Folders 1-5`.

## How to Contribute

### 1. Reporting Bugs

- Use the Issues tab on GitHub.
- If it's a logic error, paste the `[Step Id]` where the agent failed.

### 2. Adding a New Skill

1. Create a directory in `.gemini/skills/<skill-name>`.
2. Add a `SKILL.md` with the metadata frontmatter.
3. Add a `prompt.md` with the system instruction.

### 3. Code Style

- **Python**: PEP 8. Use `utils` for file I/O.
- **Markdown**: GitHub Flavored Markdown.
- **Tests**: Add unit tests in `tests/` for any new logic.

### 4. Pull Requests

- Ensure all tests pass: `python tests/test_structure.py`
- Update `KERNEL.md` if you are changing core routing logic.

## License

MIT
