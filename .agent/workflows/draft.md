---
description: Create placeholder documents (PRDs, Specs, Memos) that evolve as context is added.
---

# /draft - Progressive Document Factory

**Trigger**: User wants to start a document before having all the details.

## Steps

1.  **Intent Clarification**:
    - Ask: "What type of document?" (PRD, Spec, Memo, One-Pager)
    - Ask: "Which Company/Product?"

2.  **Stub Creation**:
    - Use template from `.agent/templates/docs/draft-prd.md` (or equivalent).
    - Create file in `2. Products/[Company]/drafts/[Product]_[DocType]_DRAFT.md`.
    - Mark as `Status: [DRAFT]`.

3.  **Accumulation Mode**:
    - Subsequent `/dump` inputs related to this document → Append to "Details Pending" section.
    - User can run `/draft update [DocName]` to review accumulated notes.

4.  **Promotion**:
    - When ready, run `/draft promote [DocName]`.
    - System moves file from `drafts/` to the main product folder.
    - Changes status to `[REVIEW]`.

## Output

- Confirmation: `Created draft: [Filename]`
- Link to the new file.

## Example

```
User: /draft
Agent: What type? (PRD, Spec, Memo)
User: PRD
Agent: Which product?
User: Company A / Product X
Agent: ✅ Created: 2. Products/Company A/drafts/ProductX_PRD_DRAFT.md
```
