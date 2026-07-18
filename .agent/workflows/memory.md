---
title: Product Memory Consolidation
description: Perform memory reflection, consolidate facts and scenarios, update the Mermaid state graph, and clear trace logs.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.

1. Ingest existing memory state from `SESSION_MEMORY.md` and L1 facts.
2. Run `python system/scripts/agentic_memory.py consolidate` to process and archive any unconsolidated L0 traces.
3. Review current session interactions and extract new L1 Atomic Facts.
   - Run `python system/scripts/agentic_memory.py add-fact "<content>" --category "<category>"` for each new fact.
4. Update nodes and edges of the Symbolic Short-Term Memory graph to match the latest task/system dependencies:
   - Run `python system/scripts/agentic_memory.py update-graph --add-node "<ID>" "<LABEL>" --add-edge "<SRC>" "<DST>" "<LABEL>"` to reflect current states.
5. Save the consolidation scenario to L2:
   - Run `python system/scripts/agentic_memory.py add-scenario "Manual Memory Sweeper" "User triggered manual consolidation and graph update."`
6. Output a summary showing the updated Mermaid graph and the count of facts/scenarios.
