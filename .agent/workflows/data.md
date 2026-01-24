---
description: Analyze data.
---

# /data - Analytics & Metrics

**Trigger**: User types `/data` or asks for metrics.

## Steps

1. **Define Intent**: Is this a _Creation_ task (define success metrics) or _Analysis_ task (query data)?
2. **Execute (Parallel Context)**:
   - IF Creation: Update the PRD with a "Success Metrics" table.
   - IF Analysis:
     - **Action**: In a SINGLE turn, read `1. Company/Metrics/` (if exists) AND scan `5. Trackers/` for relevant data points.
     - **Goal**: Write SQL or simulate a funnel analysis based on this cross-referenced context.
3. **Visualize**: Present output in a table or ASCII chart.
