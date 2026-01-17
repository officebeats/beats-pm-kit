# PM Brain Workflow Preferences

> Defines how the AI agent should behave when generating content or executing tasks.

## General Behavior

| Preference | Setting |
| :--- | :--- |
| **Verbosity** | Succinct. No fluff. Tables over prose. |
| **Confirmation** | Confirm before bulk actions (creating multiple files). |
| **Error Handling** | If unclear, park in `BRAIN_DUMP.md` instead of asking 20 questions. |
| **Source Preservation** | Always preserve raw source text when extracting insights. |

---

## Brief Generation

- **Format**: Table-based, scannable.
- **Priority Order**: Boss requests → Critical bugs → Stale items → Blocked → Calendar → Wins.
- **Length**: As short as possible while covering critical items.
- **Location**: `3. Meetings/daily-briefs/YYYY-MM-DD-[time].md`

---

## Tracker Updates

- **Auto-ID**: When creating new items, auto-assign the next sequential ID.
- **Cross-Reference**: Link related items by ID.
- **Timestamps**: Update `Last Updated` fields when modifying trackers.

---

## Documentation Style

- **Framework**: Use "Concept / Requirements / User Journey / Questions & Tasks" for strategy docs.
- **Headings**: Use `#`, `##`, `###` hierarchy.
- **Tables**: Preferred for structured data.
- **Emojis**: Use sparingly for visual scanning (🔥, ⚡, 📌, 📋).

---

## File Operations

| Action | Behavior |
| :--- | :--- |
| **Create** | Use lowercase-hyphenated names for new files. |
| **Move** | Preserve original content; update any cross-references. |
| **Delete** | Confirm with user before deleting any file. |

---

## Git Operations

- **Commit Messages**: Use conventional commit format (`feat:`, `fix:`, `chore:`).
- **Never Push**: User data folders (1-5) are local-only.
- **Auto-Update**: `#update` runs `git pull` to fetch latest system logic.
