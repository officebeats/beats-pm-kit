# Defect, Observation & Exploratory Probe Catalog (`20261014-happy-path-v2`)

## Tier 1 — Reproduced Inline During Clean Happy Path Run

### 1. `DEF-03`: Mill Admin `Edit Order` Modal `-1 Day` Timezone Shift (`11/20/2026 → 11/19/2026`)
- **Severity**: High (Data Corruption Risk if Confirmed)
- **Evidence**:
  - **BEFORE**: `evidence/step2_1_before_pending_table.png`, `evidence/def03_1_before_row_1120.png` (`Scheduled Delivery Date = 11/20/2026`)
  - **DURING (`INPUT_STAGED` / `REACTION`)**: `evidence/def03_2_modal_during_1119_shift.png`, `evidence/hyp03_admin_edit_modal_calendar.png` (`textbox "Delivery Date": 11/19/2026`)
  - **AFTER (`Cancel`)**: `evidence/def03_4_after_cancel_row_1120.png`, `evidence/step2_4_after_confirmed_table.png` (`11/20/2026` preserved by clicking `Cancel`)
- **Expected vs. Actual**: Opening the pencil `Edit Order` modal on the `11/20/2026` row should pre-fill `11/20/2026`, but pre-fills `11/19/2026` (`-1 day` in `America/Chicago` UTC-5).

### 2. `DEF-04`: Mill Admin Status Filter Pagination Trap on Page > 1
- **Severity**: Medium (UX / Navigation Trap)
- **Evidence**:
  - **BEFORE**: `evidence/def04_1_before_page2.png` (`page=2&pageSize=10&search=zzz+Test+QA`, `Status = All`)
  - **INPUT_STAGED**: `evidence/def04_2_input_staged_dropdown.png` (`Status` filter dropdown open on Page 2)
  - **REACTION**: `evidence/def04_3_reaction_nodata_page2.png` (`statuses=CONFIRMED` while `page=2` retained → renders `"No data"` and disables `<` / `>` with only `[1]` shown)
  - **AFTER**: `evidence/def04_4_after_page1_recovery.png` (Navigating to `page=1` reveals all 4 `Confirmed` rows)

### 3. `DEF-06`: Farm Owner `/schedule-order` Immediate Queue Advancement Masks Submitted Order
- **Severity**: Medium (UX Confusion / Double-Submit Inducer)
- **Evidence**:
  - **BEFORE**: `evidence/step1_1_before_cards.png` (`Estimated Delivery - 10/30/2026`, `Previous Amount Requested: 24 Tons`)
  - **INPUT_STAGED**: `evidence/step1_2_input_staged_1120.png` (`Delivery Date: 11/20/2026`)
  - **REACTION**: `evidence/step1_3_reaction_toast.png` (`alert: "Saved successfully"`, card immediately shows `10/30/2026` and `10 Tons`)
  - **AFTER**: `evidence/step1_4_after_reload_cards.png`, `evidence/step1_5_fo_home_nov_pending_chip.png` (`11/20/2026` orange Pending chip on November calendar while card binds to next `Unscheduled` `10/30/2026` `10 Tons` row)

### 4. `DEF-08`: Mill Admin Inline `Status` Dropdown (`Pending → Confirmed`) Shows Zero Toast & Leaves Row in `Pending` View Until Reload
- **Severity**: Low/Medium (UX Feedback Gap)
- **Evidence**: `evidence/step2_2_input_staged_status_dropdown.png` → `evidence/step2_3_reaction_silent_no_toast.png` → `evidence/step2_4a_pending_after_reload.png` → `evidence/step2_4_after_confirmed_table.png`.

### 5. `OBS-01..07` & `HYP-01..08`: Verified Parity & Exploratory Findings
- **`OBS-01`**: Driver `Delivery Date` input is `disabled` and locked to `10/14/2026` (`TODAY`), with zero scale ticket field (`evidence/step3_1b_modal_open_blank.png`, `evidence/step3_2_input_staged_49000_lbs.png`).
- **`OBS-02`**: Mill Admin `Edit Order` modal has no `Driver` or `Status` field (`evidence/hyp03_admin_edit_modal_calendar.png`).
- **`OBS-03` / `HYP-03`**: Farm Owner `/schedule-order` datepicker disables Saturdays/Sundays (`evidence/obs03_step1_calendar_popup_oct.png`), whereas Mill Admin `Edit Order` datepicker leaves Saturdays/Sundays clickable (`hyp03_admin_edit_modal_calendar.txt`).
- **`OBS-04`**: Farm Owner `/order-history` only displays `Last Delivery Date` (`10/14/2026`) but sorts rows by `Scheduled Delivery Date` (`11/20/2026`), inserting our new `10/14/2026 | 24.5` row at **Row 5** between two `10/11/2026` rows whose scheduled dates are `11/23/2026` and `11/19/2026` (`evidence/step4_1_after_fo_history_unfiltered.png`, `evidence/step6_2_after_admin_delivered.png`).
- **`OBS-05`**: `/home` Alerts remain pinned to earliest unfulfilled order (`10/21/2026` Pending, `10/23/2026` Unscheduled) (`evidence/step5_1_after_fo_home_oct.png`).
- **`OBS-06` / `HYP-02`**: `/schedule-order` card reads `Last Delivery Date: N/A` from the static `Unscheduled` order row even after `/my-feeds` updates to `Last Delivery Date: 10/14/2026 | Weight Delivered: 24.5 Tons` (`evidence/step5_5_after_fo_my_feeds.png`, `evidence/step5_6_after_fo_schedule_order.png`).
- **`HYP-06`**: Clicking `Edit` on Driver `Delivery Confirmation` preserves `49,000` in `Weight Delivered` (`evidence/hyp06_driver_edit_button_preserves_weight.png`).
- **`HYP-07`**: Clicking `Proceed` with blank `Weight Delivered` blocks submission with inline error `"Enter weight"` (`evidence/hyp07_driver_blank_weight_validation.png`).
- **`HYP-08`**: On Mill Admin `Delivered` rows, inline `Status` and `Remind` are `disabled`, while the green pencil `Edit` icon remains clickable (`evidence/hyp08_admin_delivered_right_cols.png`).

## Tier 2 — Historical / Gated Defects (`HISTORICAL / NOT REPRODUCED THIS RUN`)
- **`DEF-02`** (Direct `/orders/calendar/view` blank render), **`DEF-05`** (Duplicate same-day schedule from `/schedule-order`), **`DEF-07`** (Mill Admin `Edit Order` save blocked by same-day duplicate rule), **`DEF-09`** (Non-20-lb Driver input `777 lb → 780 lb / 0.39t` visible in historical `T0` rows), and **`DEF-12`** (`howlett.feedx.ag` multi-tab persona conflict, prevented by sequential single-tab execution; storage mechanism is `[INFERENCE]`).
