---
title: Optional Pack Manager
description: List, enable, disable, or run optional Beats PM capabilities kept dormant in this repository.
---

# Optional Pack Manager

Use `/pack` to manage optional capabilities without installing another repository.

## Commands

```text
/pack list
/pack status [pack-id]
/pack enable <pack-id>
/pack disable <pack-id>
/pack run <pack-id> [pack arguments]
```

Run the matching local command through `python3 system/scripts/pack_manager.py`. Disabled packs must not participate in normal workflow routing or task management.
