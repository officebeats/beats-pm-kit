# FeedX Cross-Role Weight & Date Bug Tickets for Ahmed (Validated 2026-10-14)

- **Prepared for:** Ernesto Rodriguez -> Ahmed (FeedX Engineering)
- **Test Environment:** Production QA (`admin.feedx.ag` + `howlett.feedx.ag`, `America/Chicago` UTC-5)
- **Test Entities Only:** `zzz Test QA FARM (Ernesto)` (`9a9xJ-AA-A-FMXG59c-cy`), `Cornmeal (QA Test) Ernesto`, `SSO Test`, `QA Kickoff Blend 10-14`, `Canola Meal`, Driver `QA Test Driver (Ernesto)`
- **Evidence Standard:** 73 unique live GUI screenshots (`0` duplicate MD5 hashes) across all 3 roles (`Mill Admin`, `Farm Owner`, `Truck Driver`) with 4-Frame (`BEFORE -> INPUT_STAGED -> REACTION -> AFTER_DIFF`) visual proof.

---

## Executive Summary: Why Weights & Dates Do Not Match Across Screens and Roles

Manual non-Playwright GUI testing across **Mill Admin**, **Farm Owner**, and **Truck Driver** proved **12 concrete weight, date, and state-sync bugs** fall into **4 systemic categories**:

| Category | What Happens Across Roles & Screens | Tickets |
| :--- | :--- | :--- |
| **1. Weight Unit, Rounding & Validation Mismatches (`Pounds` vs. `Tons`)** | Driver inputs weight in **Pounds** (`777 lbs`), `Delivery Confirmation` shows `777 Pounds`, Driver `Delivery History` rounds to **20-lb increments (`780 lbs`)**, and Farm Owner / Mill Admin show **0.01-Ton increments (`0.39 Tons`)**. Typing `24.5` (thinking Tons) records `0.01 Tons` (`20 lbs`). Typing **`0` Pounds** bypasses validation and advances to `Delivery Confirmation` (`0 Pounds`). | **TICKET-01 (`DEF-09`)**<br/>**TICKET-02 (`HYP-07`)** |
| **2. `/schedule-order` Card Data-Binding & Forecast Math Bugs** | `/schedule-order` cards do **not** show the farm's actual `Last Delivery Date` or `Previous Amount Requested` from completed orders — they display fields from the next `Unscheduled` row (`Last Delivery Date: N/A` on `Cornmeal` and `SSO Test`; `Previous Amount Requested: 10 Tons` even right after a `24.5 Ton` delivery). `Remaining feed for N day(s)` is `(Estimated Delivery - TODAY)` and ignores `Tons / Feeding Rate` and live `Feeding Rate` edits. Three interleaved `Unscheduled` Cornmeal series (`24t`, `10t`, `24.5t` across 45 `Unscheduled` rows) cause the card to immediately surface another `10/30/2026` row after scheduling. | **TICKET-03 (`DEF-06`)**<br/>**TICKET-04 (`OBS-06 / HYP-02`)**<br/>**TICKET-05 (`HYP-01`)**<br/>**TICKET-06 (`HYP-09 / HTML IDs`)** |
| **3. Cross-Role Date Shifts (`-1 Day` UTC Bug) & Same-Day Collision Trap** | Opening `Edit Order` in Mill Admin shifts every `Scheduled Delivery Date` **1 day earlier** (`11/20 -> 11/19`, `10/23 -> 10/22`). Clicking `Confirm` in `Edit Order` when the shifted or target date has another row for the same feed triggers red toast `"Cannot have multiple orders of the same product on the same day."` (`DEF-07`), while Farm Owner `/schedule-order` allows scheduling duplicate same-day `Pending` orders (`DEF-05`). | **TICKET-07 (`DEF-03`)**<br/>**TICKET-08 (`DEF-07 & DEF-05`)**<br/>**TICKET-09 (`HYP-03`)** |
| **4. `Scheduled Delivery Date` vs. `Last Delivery Date` Desync, Hidden Sort Order & Broken Views** | Driver delivery locks `Delivery Date = TODAY (10/14/2026)`. Driver `Delivery History` sorts by `Delivery Date DESC` (putting all four `10/14/2026` deliveries at Rows 1-4 on Page 1), whereas Farm Owner `/order-history` displays **only** `Last Delivery Date` (`10/14/2026`) **while sorting by the hidden `Scheduled Delivery Date`**, scattering the four `10/14/2026` deliveries across **Page 1 (Rows 5, 7) and Page 2 (Rows 12, 16)**! Meanwhile, `/home` Alerts still shows `Unscheduled | Next Delivery - 10/23/2026 (8 days)` when `/schedule-order` shows `10/30/2026 (15 days)`, Mill Admin `/calendar` renders **0 orders**, and `/orders/calendar/view` renders a **blank white screen**. | **TICKET-10 (`OBS-01 & OBS-04`)**<br/>**TICKET-11 (`OBS-05 / Alert Desync`)**<br/>**TICKET-12 (`DEF-02 / DEF-04 / DEF-08 / Admin Calendar`)** |

---

## Master Cross-Role Weight & Date Reconciliation Table (All 16 Delivered Rows Aligned Across All 3 Roles)

Below is the complete, multi-page 1-to-1 alignment of all **16 `Delivered` orders** for `zzz Test QA FARM (Ernesto)` across **Mill Admin `/order-management` (Page 1, 16 rows)**, **Farm Owner `/order-history` (Page 1 Rows 1-10 + Page 2 Rows 11-16)**, and **Driver `/truck-driver/delivery-history` (Page 1 Rows 1-10 + Page 2 Rows 11-15)**:

| Mill Admin `Delivered` Row # | Feed Name | Mill Admin `Scheduled Delivery Date` (Hidden Sort Key!) | Mill Admin `Last Delivery Date` | Mill Admin `Weight Ordered (Tons)` | Mill Admin `Weight Delivered (Tons)` | Farm Owner `/order-history` Page & Row (`Last Delivery Date` \| `Tons`) | Driver `/truck-driver/delivery-history` Page & Row (`Delivery Date` \| `Pounds`) | Discrepancy Note |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | `QA Kickoff Blend 10-14` | `11/05/2026` | `10/13/2026` | `15` | `17` | **Page 1, Row 1:** `10/13/2026 \| 17` | **Page 1, Row 5:** `10/13/2026 \| 34,000` | `34,000 lb = 17 Tons` |
| **2** | `QA Kickoff Blend 10-14` | `11/04/2026` | `10/13/2026` | `15` | `16.5` | **Page 1, Row 2:** `10/13/2026 \| 16.5` | **Page 1, Row 6:** `10/13/2026 \| 33,000` | `33,000 lb = 16.5 Tons` |
| **3** | `Cornmeal (QA Test) Ernesto` | `12/02/2026` | `10/11/2026` | `24` | `24` | **Page 1, Row 3:** `10/11/2026 \| 24` | **Page 1, Row 9:** `10/11/2026 \| 48,000` | `10/11` ranks above `10/14` because `12/02 > 11/20`! |
| **4** | `Cornmeal (QA Test) Ernesto` | `11/23/2026` | `10/11/2026` | `24` | `24` | **Page 1, Row 4:** `10/11/2026 \| 24` | **Page 1, Row 10:** `10/11/2026 \| 48,000` | `10/11` ranks above `10/14` because `11/23 > 11/20`! |
| **5** | `Cornmeal (QA Test) Ernesto` | **`11/20/2026`** | **`10/14/2026`** | **`24`** | **`24.5`** | **Page 1, Row 5:** `10/14/2026 \| 24.5` | **Page 1, Row 1:** `10/14/2026 \| 49,000` | **This run's delivery (`49,000 lb = 24.5t`): Row 1 in Driver, Row 5 in Farm Owner!** |
| **6** | `Cornmeal (QA Test) Ernesto` | `11/19/2026` | `10/11/2026` | `24` | `24` | **Page 1, Row 6:** `10/11/2026 \| 24` | **Page 2, Row 11:** `10/11/2026 \| 48,000` | Pre-existing `11/19` Delivered row |
| **7** | `Cornmeal (QA Test) Ernesto` | `10/23/2026` | `10/14/2026` | `10` | **`0.01`** | **Page 1, Row 7:** `10/14/2026 \| 0.01` | **Page 1, Row 4:** `10/14/2026 \| 20` | **Driver typed `24.5` (thinking Tons) -> `0.01 Tons` / `20 Pounds`!** |
| **8** | `Canola Meal` | `10/20/2026` | `10/11/2026` | `24` | `24` | **Page 1, Row 8:** `10/11/2026 \| 24` | **Page 2, Row 12:** `10/11/2026 \| 48,000` | `48,000 lb = 24 Tons` |
| **9** | `Canola Meal` | `10/13/2026` | `10/09/2026` | `24` | `24` | **Page 1, Row 9:** `10/09/2026 \| 24` | **Page 2, Row 13:** `10/09/2026 \| 48,000` | `48,000 lb = 24 Tons` |
| **10** | `Canola Meal` | `10/09/2026` | `10/08/2026` | `24` | `24` | **Page 1, Row 10:** `10/08/2026 \| 24` | **Page 2, Row 15:** `10/08/2026 \| 48,000` | `48,000 lb = 24 Tons` |
| **11** | `Cornmeal (QA Test) Ernesto` | `10/22/2026` | `10/13/2026` | `24` | `24.5` | **Page 2, Row 11:** `10/13/2026 \| 24.5` | **Page 1, Row 8:** `10/13/2026 \| 49,000` | On Page 2 in Farm Owner despite `10/22 > 10/09`! |
| **12** | `Cornmeal (QA Test) Ernesto` | `10/20/2026` | **`10/14/2026`** | `24` | **`0.39`** | **Page 2, Row 12:** `10/14/2026 \| 0.39` | **Page 1, Row 2:** `10/14/2026 \| 780` | **Driver typed `777` lbs -> `780 lbs` (Driver Page 1 Row 2) vs `0.39 Tons` (Farm Owner Page 2 Row 12)!** |
| **13** | `Cornmeal (QA Test) Ernesto` | `10/18/2026` | `10/13/2026` | `10` | `0.01` | **Page 2, Row 13:** `10/13/2026 \| 0.01` | **Page 1, Row 7:** `10/13/2026 \| 20` | `24.5 lb -> 0.01 Tons / 20 lbs` |
| **14** | `Canola Meal` | `09/29/2026` | `10/09/2026` | `24` | `24` | **Page 2, Row 14:** `10/09/2026 \| 24` | **Page 2, Row 14:** `10/09/2026 \| 48,000` | `48,000 lb = 24 Tons` |
| **15** | `Cornmeal (QA Test) Ernesto` | `10/18/2026` | `10/11/2026` | `444` | `24` | **Page 2, Row 15:** `10/11/2026 \| 24` | *(Not in QA Driver list)* | Historical seed row (`Ordered: 444 Tons`) |
| **16** | `SSO Test` | `09/26/2026` | **`10/14/2026`** | `444` | **`0.39`** | **Page 2, Row 16:** `10/14/2026 \| 0.39` | **Page 1, Row 3:** `10/14/2026 \| 780` | **Driver typed `777` lbs -> `780 lbs` (Driver Page 1 Row 3) vs `0.39 Tons` (Farm Owner Page 2 Row 16)!** |

---

## Copy-Pasteable Bug Tickets for Ahmed (`TICKET-01` to `TICKET-12`)

### TICKET-01 (`DEF-09`): Driver Weight Input (`Pounds`) Rounds to 20-lb Increments (`777 -> 780 lbs`) and Displays as `Tons` (`0.39 Tons`) Without Dual-Unit Context
- **Severity:** High (Data Integrity & Cross-Role Weight Mismatch)
- **Roles & Screens Affected:**
  1. **Driver:** `https://howlett.feedx.ag/truck-driver/home` (`Confirm Delivery` & `Delivery Confirmation` modals) and `/truck-driver/delivery-history`
  2. **Farm Owner:** `https://howlett.feedx.ag/order-history` and `/my-feeds`
  3. **Mill Admin:** `https://admin.feedx.ag/order-management` (`Status = Delivered`)
- **Screenshots:** `def09_3_confirm_summary_777_lbs.png`, `step3_4_after_driver_history.png`, `step4_2_after_fo_history_page2.png`, `step6_2_after_admin_delivered.png`
- **What You Expected:**
  - When a driver enters `777` Pounds (or `24.5` Tons), the exact weight entered by the driver is preserved across Driver `Delivery History`, Farm Owner `Order History`, and Mill Admin `Order Management`, and the unit (`Pounds` vs `Tons`) is clearly reconciled so drivers do not enter `24.5` into a `Pounds` input.
- **What You Saw Instead:**
  1. **Non-20-lb Quantization (`777 lbs -> 780 lbs / 0.39 Tons`):** In the `Confirm Delivery` modal (`def09_3_confirm_summary_777_lbs.png`), typing `777` Pounds displays `777 Pounds` in the confirmation step. Once submitted (`10/14/2026` rows for `Cornmeal` and `SSO Test`), Driver `Delivery History` (`step3_4_after_driver_history.png` Rows 2 & 3) displays **`780`** (`+3 lbs`), while Farm Owner `/order-history` (`step4_2_after_fo_history_page2.png` Rows 12 & 16) and Mill Admin `Delivered` (`step6_2_after_admin_delivered.png` Rows 12 & 16) display **`0.39` Tons** (`[INFERENCE: backend converts Pounds / 2000 = 0.3885 Tons, rounds to 2 decimal places = 0.39 Tons, and multiplies 0.39 * 2000 = 780 Pounds for Driver History]`).
  2. **Tons-vs-Pounds Unit Trap (`24.5 -> 0.01 Tons / 20 Pounds`):** Every screen in Farm Owner and Mill Admin uses **Tons** (`24 Tons`, `10 Tons`), and the `Confirm Delivery` modal does not display the order's `Weight Ordered (Tons)`. When a tester/driver enters `24.5` into `Weight Delivered (Pounds)` thinking it is Tons, it records **`0.01` Tons** in Farm Owner/Mill Admin and **`20` Pounds** in Driver `Delivery History` (`step3_4_after_driver_history.png` Row 4).

---

### TICKET-02 (`HYP-07`): Driver `Confirm Delivery` Modal Allows `0 Pounds` Delivery Without Validation Error
- **Severity:** High (Missing Input Guardrail)
- **Role & Screen Affected:** **Driver** (`https://howlett.feedx.ag/truck-driver/home` -> `Confirm Delivery` -> `Delivery Confirmation`)
- **Screenshots:** `hyp07_driver_blank_weight_validation.png`, `hyp07_2_zero_weight_reaction.png`, `def09_2_input_staged_777_lbs.png`
- **What You Expected:**
  - Entering `0` Pounds and clicking `Proceed` should be blocked with an inline validation error (e.g., `"Weight must be greater than 0"`), just as leaving the input blank blocks `Proceed` with `"Enter weight"` (`hyp07_driver_blank_weight_validation.png`).
- **What You Saw Instead:**
  - Typing `0` into `Weight Delivered (Pounds)` (`hyp07_2_zero_weight_reaction.png`) and clicking **`Proceed`** passes validation and opens the **`Delivery Confirmation`** modal (`def09_2_input_staged_777_lbs.png`) showing **`Weight Delivered : 0 Pounds`** with an active green **`Confirm`** button.

---

### TICKET-03 (`DEF-06`): Scheduling a `/schedule-order` Card Immediately Surfaces the Next `Unscheduled` Row (Including Duplicate Same-Date Series), Making Date & Weight Look Reverted
- **Severity:** High (Confusing Farm Owner UX & Duplicate Order Risk)
- **Roles & Screens Affected:** **Farm Owner** (`https://howlett.feedx.ag/schedule-order`) & **Mill Admin** (`https://admin.feedx.ag/order-management?statuses=UNSCHEDULED`)
- **Screenshots:** `step1_1_before_cards.png`, `step1_2_input_staged_1120.png`, `step1_3_reaction_toast.png`, `step1_4_after_reload_cards.png`, `step0_admin_unscheduled.png`, `step0_admin_unscheduled_page2.png`
- **What You Expected:**
  - After selecting `11/20/2026` on the `Cornmeal (QA Test) Ernesto` card and clicking `Schedule Order` (`"Saved successfully"`), `/schedule-order` should either remove the card or show that `11/20/2026` is now `Pending confirmation`.
- **What You Saw Instead:**
  - Because `zzz Test QA FARM (Ernesto)` has **45 `Unscheduled` rows across 2 pages** (`25` on Page 1 + `20` on Page 2) containing **three overlapping Cornmeal forecast series (`24 Tons`, `10 Tons`, and `24.5 Tons`)**, consuming the `10/30/2026 (24 Tons)` row in Step 1 (`step1_1_before_cards.png`) immediately surfaced the second `10/30/2026 (10 Tons)` `Unscheduled` row (`step1_4_after_reload_cards.png`, from Page 2 Row 17 of `Unscheduled`).
  - To the Farm Owner, the card still says **`Estimated Delivery - 10/30/2026`** with the date input reset to **`10/30/2026`** and `Previous Amount Requested` abruptly changed from **`24 Tons` to `10 Tons`** — tricking users into thinking their schedule action failed and causing them to click `Schedule Order` a second time.

---

### TICKET-04 (`OBS-06 / HYP-02`): `/schedule-order` Cards Display `Last Delivery Date: N/A` and Misleading `"Previous Amount Requested"` That Disagree With `/my-feeds` and `/order-history`
- **Severity:** Medium (Cross-Screen Weight & Date Disagreement)
- **Roles & Screens Affected:** **Farm Owner** (`/schedule-order` vs. `/my-feeds` vs. `/order-history`) & **Mill Admin** (`/order-management?statuses=UNSCHEDULED`)
- **Screenshots:** `step5_5_after_fo_my_feeds.png`, `step5_6_after_fo_schedule_order.png`, `step4_1_after_fo_history_unfiltered.png`
- **What You Expected:**
  - `Last Delivery Date` and `Previous Amount Requested` on `/schedule-order` should match the farm's actual last delivery on `/my-feeds` and `/order-history`.
- **What You Saw Instead:**
  | Feed Name | Farm Owner `/my-feeds` (`Last Delivery Date` \| `Weight Delivered`) | Farm Owner `/order-history` Latest Delivery | Farm Owner `/schedule-order` (`Last Delivery Date` \| `Previous Amount Requested`) |
  | :--- | :--- | :--- | :--- |
  | **`Cornmeal (QA Test) Ernesto`** | **`10/14/2026` \| `24.5 Tons`** | `10/14/2026 \| 24.5 Tons` (Ordered `24 Tons`) | **`N/A` \| `10 Tons`** (was `N/A \| 24 Tons` before Step 1; and `10/20/2026` future date on `10/26` card in manual run!) |
  | **`SSO Test`** | **`10/13/2026` \| `15 Tons`** | `10/14/2026 \| 0.39 Tons` & `10/13/2026 \| 15 Tons` | **`N/A` \| `5 Tons`** |
  | **`QA Kickoff Blend 10-14`** | **`10/13/2026` \| `17 Tons`** | `10/13/2026 \| 17 Tons` | **`10/13/2026` \| `15 Tons`** |
  | **`Canola Meal`** | **`10/11/2026` \| `24 Tons`** | `10/11/2026 \| 24 Tons` | **Missing from `/schedule-order`** (its `Unscheduled` rows are `12/29/2026` & `01/18/2027`) |

---

### TICKET-05 (`HYP-01`): `Remaining feed for N day(s)` Badge Ignores Weight/Feeding-Rate Math and Does Not Recalculate When `Feeding Rate` Is Changed
- **Severity:** Medium (Broken Forecast Math & Non-Reactive UI)
- **Role & Screen Affected:** **Farm Owner** (`https://howlett.feedx.ag/schedule-order`)
- **Screenshots:** `step5_6_after_fo_schedule_order.png`, `hyp01_2_input_staged_feeding_rate_10.png`, `hyp01_4_after_restored_rate_5.png`
- **What You Expected:**
  - The `/schedule-order` page header states: *"Please make any adjustments needed to feeding rate to accurately project when your next load will be needed."*
  - `Remaining feed for N day(s)` should reflect `Weight / Feeding Rate` (or current silo inventory), and changing `Feeding Rate` should update the projected date / remaining days.
- **What You Saw Instead:**
  1. `SSO Test` shows `5 Tons` at `2 Tons/day` (`2.5 days` of feed) and `24.5 Tons` delivered on `10/14` (`0.39t`), yet displays **`Remaining feed for 8 day(s)`** (`10/23 - 10/15`).
  2. `Cornmeal` shows `10 Tons` at `5 Tons/day` (`2 days` of feed) and `24.5 Tons` delivered on `10/14` (`4.9 days` of feed), yet displays **`Remaining feed for 15 day(s)`** (`10/30 - 10/15`).
  3. Changing `Feeding Rate` on `Cornmeal` from `5` to **`10` Tons/day** (`hyp01_2_input_staged_feeding_rate_10.png`) leaves `Remaining feed for 15 day(s)` and `Estimated Delivery - 10/30/2026` completely unchanged.

---

### TICKET-06 (`HYP-09 & Duplicate DOM IDs`): Active `Canola Meal` Feed Missing from `/schedule-order`, and Duplicate HTML `id`/`for` Attributes Across Cards Break Input Labels
- **Severity:** Low / Accessibility & UX
- **Role & Screen Affected:** **Farm Owner** (`https://howlett.feedx.ag/schedule-order` vs `/my-feeds`)
- **Screenshots:** `step5_5_after_fo_my_feeds.png`, `step5_6_after_fo_schedule_order.png`, `step0_admin_unscheduled_page2.png`
- **What You Saw:**
  1. `Canola Meal` is active in `/my-feeds` (`Last Delivery Date: 10/11/2026`, `24 Tons`) and has two `Unscheduled` rows in Mill Admin (`12/29/2026` on Page 2 Row 9 and `01/18/2027` on Page 1 Row 17), plus `Confirmed` (`11/17/2026`) and `Pending` (`11/25/2026`) orders, but renders **no card** on `/schedule-order` (with no message explaining that its next unscheduled load is beyond the display horizon).
  2. All three cards on `/schedule-order` reuse identical HTML `id` attributes for `Delivery Date`, `Feeding Rate`, and `Delivery Slot`, causing all three `<label>` tags on the page to bind to Card 1 (`SSO Test`: accessible name `"Feeding Rate Feeding Rate Feeding Rate"`) while Cards 2 (`Cornmeal`) and 3 (`QA Kickoff Blend 10-14`) have unlabelled inputs.

---

### TICKET-07 (`DEF-03`): Mill Admin `Edit Order` Modal Pre-Fills `Delivery Date` 1 Day Earlier (`-1 Day` UTC Offset Bug)
- **Severity:** High (Data Corruption Risk)
- **Role & Screen Affected:** **Mill Admin** (`https://admin.feedx.ag/order-management` -> Pencil `Edit` Icon -> `Edit Order` Modal)
- **Screenshots:** `def03_1_before_row_1120.png`, `def03_2_modal_during_1119_shift.png`, `def03_4_after_cancel_row_1120.png`, `def07_1_before_pending_1023.png`, `def07_3_reaction_red_toast.png`
- **What You Expected:**
  - Opening `Edit Order` on a row with `Scheduled Delivery Date = 11/20/2026` (or `10/23/2026`) pre-fills `Delivery Date = 11/20/2026` (or `10/23/2026`).
- **What You Saw Instead:**
  - In `America/Chicago` (UTC-5), every `Edit Order` modal pre-fills `Delivery Date` **1 calendar day earlier**:
    - Table row `11/20/2026` -> Modal `Delivery Date` pre-fills **`11/19/2026`** (`def03_2_modal_during_1119_shift.png`).
    - Table row `10/23/2026` -> Modal `Delivery Date` pre-fills **`10/22/2026`** (`def07_3_reaction_red_toast.png`).
  - If an admin edits `Weight Order`, `Feeding Rate`, or `Delivery Time Slot` and clicks `Confirm` without noticing the `-1 day` shift, the order's scheduled date is silently overwritten to 1 day earlier.

---

### TICKET-08 (`DEF-07 & DEF-05`): Mill Admin `Edit Order` Modal `Confirm` Blocked by `"Cannot have multiple orders of the same product on the same day."` While Farm Owner `/schedule-order` Allows Duplicate Same-Day Orders
- **Severity:** High (Workflow Blocker)
- **Roles & Screens Affected:** **Mill Admin** (`/order-management` -> `Edit Order` modal) & **Farm Owner** (`/schedule-order`)
- **Screenshots:** `def07_1_before_pending_1023.png`, `def07_3_reaction_red_toast.png`, `def07_4_after_cancel_unchanged.png`, `def07_5_after_table_unchanged.png`
- **What You Expected:**
  - Same-day duplicate rules should be enforced consistently at order creation on `/schedule-order`, and Mill Admin should be able to edit an existing order's slot/weight without being blocked by a `-1 day` date shift or a duplicate row.
- **What You Saw Instead:**
  1. Farm Owner `/schedule-order` allowed scheduling two `Cornmeal` orders onto `10/23/2026` (`24 Tons` and `10 Tons`, `DEF-05`).
  2. When Mill Admin opens `Edit Order` on the `10/23/2026` (`10 Tons`) `Pending` row (`def07_1_before_pending_1023.png`), `DEF-03` shifts `Delivery Date` inside the modal to **`10/22/2026`** (`def07_3_reaction_red_toast.png`, which collides with the `10/22/2026` `24.5 Tons` row), OR if the admin re-selects `10/23/2026` (which collides with the other `10/23/2026` row), clicking **`Confirm`** fails with red toast: **`"Cannot have multiple orders of the same product on the same day."`** (`def07_4_after_cancel_unchanged.png`).

---

### TICKET-09 (`HYP-03 & OBS-03`): Weekend Dates (`Sat/Sun`) Disabled on Farm Owner `/schedule-order`, Enabled in Mill Admin `Edit Order` Modal, and Generated by Auto-Forecast (`11/29/2026` Sunday)
- **Severity:** Low / Business Rule Inconsistency
- **Roles & Screens Affected:** **Farm Owner** (`/schedule-order`), **Mill Admin** (`Edit Order` modal & `Unscheduled` forecast), **Driver** (`See Orders`)
- **Screenshots:** `obs03_step1_calendar_popup_oct.png`, `hyp03_admin_edit_modal_calendar.png`
- **What You Saw:**
  - Farm Owner `/schedule-order` disables all Saturdays and Sundays (`obs03_step1_calendar_popup_oct.png`).
  - Mill Admin `Edit Order` modal calendar (`hyp03_admin_edit_modal_calendar.png`) enables all Saturdays and Sundays (`11/01, 07, 08, 14, 15, 21, 22, 28, 29`).
  - Completed `Delivered` orders include `Scheduled Delivery Date = 10/18/2026` (**Sunday**) and `09/26/2026` (**Saturday**).

---

### TICKET-10 (`OBS-01 & OBS-04`): `Scheduled Delivery Date` Is Overwritten by `TODAY` in Driver Modal and Omitted From Farm Owner `/order-history` While Still Used as the Hidden Sort Key
- **Severity:** High (Primary Cause of Cross-Role Date Confusion After Delivery)
- **Roles & Screens Affected:**
  1. **Driver:** `/truck-driver/home` (`Confirm Delivery` modal) & `/truck-driver/delivery-history` (Pages 1-2)
  2. **Farm Owner:** `/order-history` (Pages 1-2) & `/home` Calendar
  3. **Mill Admin:** `/order-management` (`Status = Delivered`)
- **Screenshots:** `step3_1b_modal_open_blank.png`, `step3_4_after_driver_history.png`, `step3_5_driver_history_page2.png`, `step4_1_after_fo_history_unfiltered.png`, `step4_2_after_fo_history_page2.png`, `step6_2_after_admin_delivered.png`
- **What You Expected:**
  - Both Farm Owner `/order-history` and Driver `/truck-driver/delivery-history` should either display **both** `Scheduled Delivery Date` and `Actual/Last Delivery Date` (like Mill Admin `Delivered` does) or sort chronologically by the visible `Last Delivery Date` column (`10/14/2026` at the top).
- **What You Saw Instead:**
  1. **Driver Modal Locks `Delivery Date = TODAY` (`10/14/2026`):** Delivering the `11/20/2026` order forces `Delivery Date = 10/14/2026` (`disabled`, `step3_1b_modal_open_blank.png`).
  2. **Driver `Delivery History` Sorts by `Delivery Date DESC` (Rows 1-4 on Page 1):** All four `10/14/2026` deliveries (`49,000`, `780`, `780`, `20` lbs) appear at the top of Page 1 (`step3_4_after_driver_history.png`), but the `Scheduled Delivery Date` (`11/20`, `10/20`, `09/26`, `10/23`) is hidden.
  3. **Farm Owner `/order-history` Hides `Scheduled Delivery Date` But Sorts By It:** On Farm Owner `/order-history`, the visible `Last Delivery Date` column jumps non-chronologically (`10/13`, `10/13`, `10/11`, `10/11`, **`10/14`**, `10/11`, **`10/14`**, `10/11`, `10/09`, `10/08` on Page 1; `10/13`, **`10/14`**, `10/13`, `10/09`, `10/11`, **`10/14`** on Page 2)! Why? Because the API sorts `/order-history` by the **hidden `Scheduled Delivery Date`**, burying the `10/14/2026 (0.39 Tons / 780 lbs)` deliveries on **Page 2 (Rows 12 and 16)** while placing `10/14/2026 (24.5 Tons)` at **Row 5 on Page 1** underneath `10/11/2026` rows!

---

### TICKET-11 (`OBS-05 & Alert Desync`): Farm Owner `/home` Alerts Show Stale `Unscheduled | Next Delivery - 10/23/2026 (8 days)` That Contradicts `/schedule-order` (`10/30/2026, 15 days`) and Mill Admin `Unscheduled`
- **Severity:** Medium (Cross-Screen Date & Status Contradiction)
- **Roles & Screens Affected:** **Farm Owner** (`https://howlett.feedx.ag/home` `Alerts` vs. `/schedule-order`) & **Mill Admin** (`/order-management`)
- **Screenshots:** `step5_1_after_fo_home_oct.png`, `step5_6_after_fo_schedule_order.png`, `step6_3_after_admin_unscheduled.png`, `step0_admin_unscheduled_page2.png`
- **What You Expected:**
  - `/home` `Alerts` and `/schedule-order` should show the exact same next `Unscheduled` date and remaining feed days for each feed.
- **What You Saw Instead:**
  - On `/home` `Alerts` (`step5_1_after_fo_home_oct.png`), `Cornmeal (QA Test) Ernesto` displays two rows:
    1. `Pending Confirmation | Cornmeal (QA Test) Ernesto | Next Delivery - 10/21/2026` (from the unfulfilled `10/21/2026` `Pending` row).
    2. **`Remaining Feed for 8 day(s) | Unscheduled | Cornmeal (QA Test) Ernesto | Next Delivery - 10/23/2026`** — even though **zero** `10/23/2026` `Unscheduled` Cornmeal row exists in Mill Admin (all `45` `Unscheduled` rows across Page 1 & Page 2 start at `10/30/2026` for Cornmeal), and `/schedule-order` (`step5_6_after_fo_schedule_order.png`) displays **`Remaining feed for 15 day(s) | Estimated Delivery - 10/30/2026`**!
  - Meanwhile, `QA Kickoff Blend 10-14` has an active card on `/schedule-order` (`Remaining feed for 26 day(s) | Estimated Delivery - 11/10/2026`) and a `Confirmed` order on `10/28/2026`, yet has **zero** entry in `/home` `Alerts`.

---

### TICKET-12 (`DEF-02 / DEF-04 / DEF-08 / Admin Calendar`): Four UI State Bugs Across Farm Owner and Mill Admin (`Blank /orders/calendar/view`, `Page > 1 Filter Trap`, `Silent Inline Status Update`, `Empty Admin Calendar`)
- **Severity:** Medium (UI State & Navigation Bugs)
- **Screenshots:** `def02_2_blank_calendar_view.png`, `def04_1_before_page2.png`, `def04_3_reaction_nodata_page2.png`, `def04_4_after_page1_recovery.png`, `step2_3_reaction_silent_no_toast.png`, `hyp04_1_admin_calendar.png`
- **Observed Bugs:**
  1. **`DEF-02` (Farm Owner `https://howlett.feedx.ag/orders/calendar/view`):** Navigating directly to `/orders/calendar/view` renders a **100% blank white screen** (`def02_2_blank_calendar_view.png`, `7,552 bytes`).
  2. **`DEF-04` (Mill Admin `/order-management` Page $>1$ Filter Trap):** Changing `Status` from `All` to `Confirmed` while on Page `2` (`def04_1_before_page2.png`) does not reset `page=1`; it requests `page=2&statuses=CONFIRMED`, renders **`"No data"`** (`def04_3_reaction_nodata_page2.png`), and disables both `<` and `>` pagination arrows until the user manually clicks `1` (`def04_4_after_page1_recovery.png`).
  3. **`DEF-08` (Mill Admin Inline `Status` Dropdown):** Changing a row from `Pending` to `Confirmed` via the inline `Status` dropdown (`step2_3_reaction_silent_no_toast.png`) emits **zero toast notification** and leaves the row sitting inside the `Pending`-filtered table showing `Confirmed` until `F5` reload.
  4. **Mill Admin `/calendar` Empty (`https://admin.feedx.ag/calendar`):** Clicking `Calendar` in the Mill Admin left sidebar (`hyp04_1_admin_calendar.png`) renders an empty October 2026 grid with **0 order chips**, despite 16 `Delivered`, 6 `Pending`, 4 `Confirmed`, and 45 `Unscheduled` orders in `/order-management`.
