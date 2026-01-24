---
description: Generate a 30-second cheat sheet for a meeting or topic.
---

# /prep - The Meeting Dossier

**Trigger**: `/prep [Person Name]` or `/prep [Project Name]`

## Steps

1.  **Parallel Context Dragnet**:
    - **Action**: In a SINGLE turn:
      - Check `4. People/` (if person) OR `2. Products/` (if project).
      - Run `grep_search` on `5. Trackers/` for open tasks/decisions.
      - Run `grep_search` on `3. Meetings/transcripts/` for recent mentions.

2.  **Synthesize Dossier**:
    - **Goal**: Give me "The Edge". What do I need to know to win this interaction?
    - **Focus**:
      - Unresolved conflicts (Open P0s).
      - Promises made (Action Items).
      - Strategic Context (Recent decisions).

3.  **Output**:
    - Display the "Dossier" to the user.
