---
name: vacuum-protocol
description: System optimization, task archiving, and hierarchical integrity auditing.
triggers:
  - "/vacuum"
  - "/archive"
  - "/clean"
  - "/cleanup"
version: 1.0.0 (Native Optimized)
author: Beats PM Brain
---

# Vacuum Protocol Skill

> **Role**: System Optimizer & Data Archivist. You maintain the "Centrifuge Protocol" to ensure the brain remains lean, private, and organized.

## 1. Native Interface

- **Inputs**: `/vacuum`, `/archive`.
- **Primary Source**: `system/scripts/vacuum.py`.
- **Tools**: `run_command` (Python script).

### Runtime Capability

- **Antigravity**: Parallel archiving and integrity audits across multiple trackers.
- **CLI**: Batch processing with final status summary.

## 2. Cognitive Protocol

### A. Archive Phase (`/archive`)

1.  **Extract**: Identify all completed items (`- [x]`) in active tracker files.
2.  **Move**: Append completed items to yearly archive files in `5. Trackers/archive/`.
3.  **Index**: Update the `Global Archive Index` (`archive/INDEX.md`) with a summary entry.

### B. Cleanup Phase (`/clean`)

1.  **Logs**: Purge temporary files and keep only the last 5 vibe reports in `system/reports/`.
2.  **Transcripts**: Move transcripts older than 7 days to cold storage.

### C. Audit Phase (`/vacuum`)

1.  **Integrity**: Scan Folders 1, 2, and 4 for hierarchical violations (loose files outside product folders).
2.  **Privacy**: Cross-reference staged/untracked files against privacy rules to ensure no "Dark Matter" (Folders 1-5) is leaked.
3.  **Access**: Verify system read/write permissions for all tier-0 folders.

## 3. Output

- **Summary Table**: Display items moved, files cleaned, and audit results.
- **Health Badge**: `✅ Optimized` if all protocols pass.

## 4. Operational Guardrails

- NEVER delete active content; only move to `archive`.
- ALWAYS verify `.gitignore` status for Folders 1-5 before proceeding.
