# 🛡️ FAANG-Grade Chaos & Regression Suite (v1.4.1+)

This suite implements **Defensive Testing**, **Chaos Engineering**, and **Fuzzy State Validation** to ensure the Neural Mesh survives high-entropy enterprise environments.

---

## 🌪️ Chaos Engineering Benchmarks

| Category             | Metric          | Failure Threshold                        |
| :------------------- | :-------------- | :--------------------------------------- |
| **Recursive Depth**  | Loop Detection  | Rejected after 3 hops.                   |
| **Syntax Injection** | Table Escape    | 0% breakage of Markdown schema.          |
| **Naming Collision** | Resolution Rate | > 98% accuracy on similar entities.      |
| **Graceful Failure** | System Recovery | Manual re-read / self-heal on file lock. |

---

## 🧪 Edge Case Scenarios

### 1. Semantic Collision (The "Which One?" Test)

| ID          | Title                 | Input Signal                                                            | Expected Handling                                                         |
| :---------- | :-------------------- | :---------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **EDGE-01** | **Product Ambiguity** | "Login is broken on the app." (Folders: `mobile-ios`, `mobile-android`) | Prompts user for platform selection or checks recent history for context. |
| **EDGE-02** | **Entity Clash**      | "Mark said it's fine." (Team: `Mark S.`, `Mark D.`)                     | Checks project affiliation or prompts: "Which Mark? (S. or D.)".          |
| **EDGE-03** | **Nickname Overload** | "The Big Kahuna wants it."                                              | Fails gracefully -> Logs under `Unknown Stakeholder` + flags for Triage.  |

### 2. Syntax Malformation (The "Markdown Killer")

| ID          | Title                | Input Signal                                             | Expected Handling                                        |
| :---------- | :------------------- | :------------------------------------------------------- | :------------------------------------------------------- | ----- | ----- | ------ | ------- | ------------------------------------------------------------------------- |
| **EDGE-04** | **Pipe Injection**   | `Bug: User name                                          | with                                                     | extra | pipes | breaks | tables` | Sanitizes pipes or uses HTML entity `&#124;` to prevent table corruption. |
| **EDGE-05** | **Backtick Nesting** | ` Task: review this code: ```javascript var x = 1 ```  ` | Prevents code block bleeding into the tracker structure. |
| **EDGE-06** | **Unclosed Formats** | `Feature Request: *Bold text that never ends...`         | Self-closes formatting tags before writing to file.      |

### 3. State & Race Conditions

| ID          | Title                | Input Signal                                                         | Expected Handling                                                                    |
| :---------- | :------------------- | :------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| **EDGE-07** | **Concurrent Write** | 2 agents writing to `ACTION_PLAN.md` within 50ms.                    | File-level atomic write or retry-after-lock pattern.                                 |
| **EDGE-08** | **Recursive Loop**   | Agent A yields to Agent B, which contains a rule to trigger Agent A. | "Depth Counter" trigger: Halt and log "Critical Orchestration Error: Loop Detected". |
| **EDGE-09** | **Deleted Context**  | Tracking a bug for a Product whose `.md` file was just deleted.      | Reports "Context Missing" -> Creates `vault/products/RECOVERED-[Name].md` baseline.  |

---

## ⚡ Concurrency & Stress Scenarios

| ID            | Load Type           | Stress Pattern                                             | Validation                                                                        |
| :------------ | :------------------ | :--------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| **STRESS-01** | **Burst Ingestion** | Input 50+ lines of raw Slack chat containing 10+ bugs.     | 10+ unique IDs generated; zero loss of context.                                   |
| **STRESS-02** | **Deep Tree Scan**  | Force a `#status` command while `vault/` has 1,000+ files. | Validates lazy-loading protocol (KERNEL.md) performance; avoids context overflow. |
| **STRESS-03** | **Big Binary Drop** | Drop a 1GB MKV file in `00-DROP-FILES-HERE-00/`.           | Graceful rejection/triage: "Skipping large binary file; metadata scan only."      |

---

## 🏁 Verification Script (`system/scripts/chaos_runner.py`)

This script automates the validation of the above.

1. **Initialize Chaos**: Create 2 similarly named products and 2 similar stakeholders.
2. **Inject Malformed Input**: Send `/bug` commands with table-breaking characters.
3. **Trigger Concurrent Agents**: Simulate 3 handoffs in a single turn.
4. **Audit Structural Integrity**: Run `grep` for broken pipes or unassigned `null` entities.
