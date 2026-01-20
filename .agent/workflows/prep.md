---
description: Generate a 30-second cheat sheet for a meeting or topic.
---

# /prep - The Meeting Dossier

**Trigger**: `/prep [Person Name]` or `/prep [Project Name]`

## Steps

1.  **Identify Target**:
    - Parse the argument. Is it a Person (check `4. People/`) or a Project (check `2. Products/`)?

2.  **Activate `context-retriever`**:
    - Instruct the skill: "Mine the entire brain for trace evidence of [Target]. Look for open tasks, recent decisions, and transcript mentions."

3.  **Synthesize Dossier**:
    - **Goal**: Give me "The Edge". What do I need to know to win this interaction?
    - **Focus**:
      - Unresolved conflicts (Open P0s).
      - Promises made (Action Items).
      - Strategic Context (Recent decisions).

4.  **Output**:
    - Display the "Dossier" to the user.
