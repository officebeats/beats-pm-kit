---
title: "SOP & Operational Runbook: [Process Name]"
type: "sop"
status: "active"
owner: "[Operations Lead]"
up: "[[MOC_Company]]"
tags:
  - type/sop
  - status/active
  - area/operations
aliases:
  - "[Process Name] Runbook"
---

# ⚙️ Standard Operating Procedure: [Process Name]

> **Purpose**: [Clear statement of the operational goal and expected execution timeframe.]  
> **Trigger**: `[SCHEDULED (Weekly/Monthly) | INCIDENT | EVENT-DRIVEN]`  
> **Estimated Timebox**: `[15 mins | 1 hour]`

---

## 1. Prerequisites & Access Checklist
- [ ] Required permissions / role: `[Admin | Ops | Tech Lead]`.
- [ ] Tooling / CLI tools verified: `[Docker, kubectl, python3, etc.]`.
- [ ] Communication channel initialized: `[#war-room / #ops-announcements]`.

---

## 2. Step-by-Step Execution Checklist

### Phase 1: Preflight Verification
1. **Health Check**: Confirm upstream system metrics are green:
   ```bash
   python3 system/scripts/twg_health.py --json
   ```
2. **Snapshot State**: Capture pre-operation configuration backup.

### Phase 2: Core Execution
- [ ] **Step 1**: Execute core migration / procedure:
  ```bash
  python3 system/scripts/vacuum.py --safe
  ```
- [ ] **Step 2**: Verify output state and log artifact links.

### Phase 3: Post-Execution Verification
- [ ] Verify error logs are clean ($0$ unhandled exceptions).
- [ ] Post completion receipt to team channel.

---

## 3. Failure Recovery & Escalation Path
- **Failure Condition**: Any unhandled exception or status failure during Phase 2.
- **Immediate Rollback**:
  ```bash
  python3 system/scripts/vacuum.py --rollback
  ```
- **Escalation Contact**: `@oncall-lead` (Slack) or phone `[Emergency Ops Bridge]`.
