---
title: Trello Task Board Pack
---

# Trello Task Board Pack

This optional pack mirrors accepted Markdown task state into Trello. It never replaces the task notes in `5. Trackers/tasks/`.

## Enable

```text
/pack enable trello
```

Enabling the pack changes only ignored local configuration in `.beats/packs.json`.

## Use

Inspect before writing:

```text
/pack run trello status
/pack run trello sync --dry-run
```

Apply only when the user explicitly requests the specific Trello mutation:

```text
/pack run trello sync --apply
```

Credentials and board identifiers remain in ignored `system/config/trello_config.json`.
