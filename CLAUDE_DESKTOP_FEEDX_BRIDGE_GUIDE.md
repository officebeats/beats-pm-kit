# Claude Desktop & OMP Bridge Guide: FeedX Test Automation

> **MANDATORY CODE-REALITY DIRECTIVE (2026-10-13):** Read [`C:\Users\ErnestoRodriguez\orca\feedx-claude-bridge\ORCA_CLAUDE_CODE_REALITY_DIRECTIVE.md`](file:///C:/Users/ErnestoRodriguez/orca/feedx-claude-bridge/ORCA_CLAUDE_CODE_REALITY_DIRECTIVE.md) first. Do NOT re-introduce retired pre-access assumptions (zero Scale Ticket fields exist in `howlett.feedx.ag` or `admin.feedx.ag`; Driver `Weight Delivered` is in `Pounds` and converts to Tons via `÷ 2,000` so always enter whole Pounds like `33000`; never confirm inside Mill Admin `Edit Order` modal due to `DEF-03`; no Driver selector or `Out for Delivery` status exists; no visual silo gauge exists; use untainted feed `QA Kickoff Blend 10-14` rather than polluted `Cornmeal`).
>
> **Role Separation:**
> - **Claude Desktop (Supervisor & Auditor):** Directs test runs, provides strict validation criteria, verifies outputs, triages failures, and asks `omp` for re-runs or targeted deep-dives via the `omp_run` MCP tool.
> - **OMP (Heavy Engine & Executor):** Executes the resource-intensive Playwright browser automation, DOM audits, screenshot diffs, visual captures, and multi-viewport regression runs, writing dense structured findings to `_omp/out/`.

> **ERNESTO DIRECTIVE FOR CLAUDE & MUSE AGENTS (2026-10-15 — TODAY vs. NEXT WEEK BUG SPLIT):**
> - **Today's Active DevOps Bug Pack (7 Tickets — Create Today):** See [`AHMED_BUG_TICKETS_WEIGHTS_AND_DATES.md`](AHMED_BUG_TICKETS_WEIGHTS_AND_DATES.md) and [`AHMED_BUG_TICKETS_FOR_AHMED.html`](AHMED_BUG_TICKETS_FOR_AHMED.html) (`1` Driver weight rounds/Pounds-vs-Tons, `2` Schedule cards `Last Delivery: N/A` & wrong weight, `3` Remaining feed days ignore weight/rate changes, `4` Admin `Edit Order` modal `-1 day` shift, `5` Farm `Order History` scatters today's deliveries across Pages 1–2, `6` Active `Canola Meal` missing from `/schedule-order`, `7` Admin `/calendar` renders zero orders).
> - **Held Off for Next Week (7 Tickets — DO NOT Create DevOps Tickets Today):** See [`FEEDX_NEXT_WEEK_DEFERRED_BUGS.md`](FEEDX_NEXT_WEEK_DEFERRED_BUGS.md) and [`FEEDX_NEXT_WEEK_DEFERRED_BUGS.html`](FEEDX_NEXT_WEEK_DEFERRED_BUGS.html) (`Orig #5` `Edit Order` Confirm duplicate toast, `Orig #7` Farm `Home Alerts` contradict `/schedule-order`, `Orig #8` Weekend dates blocked for Farm / enabled for Admin, `Orig #10` `/orders/calendar/view` blank white screen, `Orig #11` Admin Page-2 status filter `"No data"`, `Orig #12` Admin inline status change no toast/refresh, `Orig #13` Admin `Delivered` rows open editable `Edit Order` modal).

---

## 1. How Claude Desktop Triggers OMP

In your Claude Desktop chat, Claude has access to the local MCP tool `omp_run`. Claude can call:

```json
{
  "task": "Execute the FeedX critical focus test suite (python system/qa/execute_critical_suite.py), capture before/during/after screenshots across both Desktop and Mobile (iPhone 14) viewports for the 7 focus areas, and provide a full defect breakdown complying with QA_DEFECT_EXPLANATION_STANDARD.md.",
  "label": "feedx-critical-qa",
  "tools": "read,grep,glob,bash,eval",
  "allow_edits": false,
  "max_minutes": 10
}
```

OMP will run headless via Edge/Chromium against `admin.feedx.ag`, save screenshots and JSON traces into `system/qa/evidence/CRITICAL_FOCUS/`, and emit a structured report into `_omp/out/<timestamp>-feedx-critical-qa.md`.

---

## 2. The 7 Critical Regression Test Areas

Claude Desktop monitors and verifies the following 7 test cases executed by OMP:

| Test ID | Focus Area | Device Viewport | Route | Verification Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-CRIT-01** | **Calendar Feature Highlight** | Desktop (1440x900) | `/calendar` | • Unified single calendar rendering active orders and projected depletion reorders.<br>• Clean toggle between **Month**, **Week**, and **Day** views.<br>• Visual density check; zero infinite spinners or overlapping event cells. |
| **TC-CRIT-02** | **Alerts & Low Feed Notifications** | Desktop (1440x900) | `/overview` | • Top navigation notification bell icon and unread count badge.<br>• Alerts popover drawer with categorical tabs (**Orders**, **Inquiries**, **Others**).<br>• Overview **Low Feed Alerts** table highlighting farms with $< 48\text{ hrs}$ grain supply in amber/red with 1-click schedule trigger. |
| **TC-CRIT-03** | **Schedule Orders Page** | Desktop (1440x900) | `/order-management` | • Consolidated location to schedule all feed products across farm silos.<br>• "Add New Order" modal validation: Farm Name, Feed Name, Weight Ordered (Tons), Feeding Rate (Tons/day), Delivery Date calendar picker, Trailer Type (Auger, Dump, Hopper, Belt/Floor).<br>• Real-time grid update without page refresh. |
| **TC-CRIT-04** | **Nutritionist Account Integration** | Desktop (1440x900) | `/customer-management` | • Farm owner or mill admin adding independent dairy nutritionist to farm team roster.<br>• Role dropdown includes `NUTRITIONIST`.<br>• `canManageOrders` toggle functionality allowing custom rations and mix inquiries. |
| **TC-CRIT-05** | **Order History & Status Lifecycle** | Desktop (1440x900) | `/order-management` | • Historical delivered orders verification (delivered weight, delivered weight in Pounds, delivery date).<br>• Status filter transitions (**Delivered**, **Confirmed**, **All**).<br>• Search persistence and immutable historical logging. |
| **TC-CRIT-06** | **Farm & Location Switcher** | Desktop (1440x900) | `/customer-management` | • Top-bar tenant/farm selector and search filter.<br>• Instant switching between distinct locations (e.g. `zzz Test QA` vs `Lizzie`).<br>• Strict multi-site isolation (silo levels, team members, and order queues isolate with zero cross-tenant bleeding). |
| **TC-CRIT-07** | **Mobile Viewport Parity** | Mobile (390x844 / iPhone 14) | `/overview` & `/calendar` | • Responsive mobile hamburger navigation and drawer menus.<br>• Zero horizontal viewport blowouts (`body.scrollWidth == window.innerWidth`).<br>• Touch-ergonomic scheduling modals and mobile calendar stacking. |

---

## 3. Multi-Role User Persona & Remembered Logins

The test suite covers the 5 dedicated user personas across the two-sided platform (`system/qa/feedx_user_roles.py`):

| Persona | Dedicated Identity & Entity | Role Claim / Mode | Boundary & Permission Gate |
| :--- | :--- | :--- | :--- |
| **1. Mill Admin / Dispatcher** | Ernesto Rodriguez (`rodriguez.ernesto@captiospartners.com`) | `ADMIN` (Tenant: `howlett`) | Full access to order dispatch, calendar blackouts, farm CRM, and batch pricing. |
| **2. Farm Owner** | QA Farm Owner (`qa-owner@feedx.test` \| Farm: `zzz Test QA (Ernesto)`) | `FARM_OWNER` | View farm silos, submit order edit requests, add team members, invite nutritionists. Blocked from other farms. |
| **3. Feeder** | QA Barn Feeder (`qa-feeder@feedx.test` \| Farm: `zzz Test QA (Ernesto)`) | `FEEDER` (via `canManageOrders`) | Can only reorder when permission toggle is ON. Blocked from financial ledgers and customer CRM (`TC-FARM-03`). |
| **4. Nutritionist** | QA Nutritionist (`qa-nutri@feedx.test`) | `NUTRITIONIST` | Submit custom mix formulations, upload formulation PDFs, inquire on custom rations (`TC-INQ-01`, `TC-CRIT-04`). |
| **5. Truck Driver** | QA Test (Ernesto) (ID: `GMQumGRrz4HxckhyV8yw8`) | `TRUCK_DRIVER` | Mobile stop manifest, farm gate proximity check-in, and certified net delivered weight logging (`TC-TMS-01`, `TC-TMS-02`). |

Tests verify that non-admin roles hit the **Role Permission Wall** (`TC-AUTH-03`) preventing unauthorized access to mill pricing or other farms' records.
---

## 4. Strict Layman Defect Reporting Standard

When OMP reports back or Claude Desktop triages any failure, the output **must** comply with `system/qa/QA_DEFECT_EXPLANATION_STANDARD.md`:
1. **Layman Explanation:** Why it failed in non-technical dispatcher/business terms.
2. **Expected vs. Observed Breakdown:** Exact screen state difference.
3. **Screenshot Proof & Visual Callout:** Pointer to `system/qa/evidence/CRITICAL_FOCUS/<TEST_ID>/[before|during|after].png`.
4. **Operational Risk / Impact:** Real-world consequence on mill dispatch, truck delivery, or dairy cows running out of grain.

---

## 5. Prompts You Can Give to Claude Desktop

You can copy and paste either of these prompts directly into **Claude Desktop**:

### Option A: Run Full Critical Suite
> *"Claude, using the local `omp_run` bridge, trigger the FeedX critical focus test suite (`python system/qa/execute_critical_suite.py`). Make sure OMP tests all 7 critical areas (Calendar, Alerts, Schedule Orders, Nutritionist Linking, Order History, Farm Toggle, and Mobile Viewport). Once OMP finishes, inspect `system/qa/evidence/CRITICAL_FOCUS/critical_suite_summary.json` and give me your supervisory verification report with any detected defects or UX gaps."*

### Option B: Deep-Dive a Single Area (e.g. Mobile or Nutritionist)
> *"Claude, call `omp_run` to inspect the FeedX mobile responsiveness on iPhone 14 (`TC-CRIT-07`) and the Nutritionist linking workflow (`TC-CRIT-04`). Audit the screenshots generated in `system/qa/evidence/CRITICAL_FOCUS/` and tell me if either fails our pre-launch standard."*
