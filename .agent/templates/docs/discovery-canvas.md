---
title: "Product Discovery Canvas: [Opportunity Area]"
type: "discovery"
status: "active"
owner: "[Discovery Lead]"
up: "[[MOC_Products]]"
tags:
  - type/discovery
  - status/active
  - area/[domain]
---

# 🔍 Product Discovery Canvas: [Opportunity Area]

> **Desired Business Outcome**: [Single measurable target outcome, e.g. *Increase 14-day user retention from 24% to 38%*]

---

## 1. Opportunity Solution Tree (OST)

```text
[ Desired Outcome: Increase 14-Day Retention $\ge 38\%$ ]
  ├── Opportunity 1: Users struggle to connect data sources on day 1
  │     ├── Solution 1A: 1-Click OAuth connector for Google Workspace
  │     └── Solution 1B: Pre-built demo sample workspace
  ├── Opportunity 2: Team invites fail due to SSO domain mismatch
  │     ├── Solution 2A: Automated domain discovery & invite prompt
  │     └── Solution 2B: Just-in-Time (JIT) SAML user provisioning
  └── Opportunity 3: Mobile users cannot review critical alerts
        └── Solution 3A: Rich push notification actions
```

---

## 2. Customer Interview Evidence Log

| Date | Customer / Persona | Verbatim Quote & Friction Signal | Linked Opportunity |
|:---|:---|:---|:---|
| 2026-08-20 | VP Sales (Acme) | *"We lost 3 days trying to invite the APAC team because SSO required manual IT approval."* | Opportunity 2 |
| 2026-08-22 | Growth Lead (Beta) | *"I opened the app, saw an empty dashboard, and didn't know what to click first."* | Opportunity 1 |

---

## 3. Risk Assumption Mapping (Pre-Mortem)

Evaluate high-priority solutions across the 4 core product risk categories:

| Solution Concept | Risk Category | Assumption Stated | Impact (H/M/L) | Uncertainty (H/M/L) | PoL Experiment |
|:---|:---|:---|:---:|:---:|:---|
| **1-Click OAuth Connector** | Value | Users trust granting workspace read permissions. | High | High | Fake-door CTA test on dashboard. |
| **1-Click OAuth Connector** | Feasibility | Google API quota supports real-time sync. | High | Med | Technical spike (48hr timebox). |
| **JIT Provisioning** | Viability | Enterprise InfoSec approves auto-provisioning. | High | High | 5 customer interviews with IT leads. |

---

## 4. Experiment Results & Next Decision Gate
- **Experiment Ran**: [Brief description of experiment]
- **Observed Signal**: [Qualitative and quantitative evidence collected]
- **Decision**: `[SHIP TO ROADMAP | PIVOT SOLUTION | KILL OPPORTUNITY]`
