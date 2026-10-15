# FeedX Held-Off Bug Pack — Slated for Next Week (7 Deferred Tickets)

> DO NOT create DevOps tickets for these 7 items today. Held off for next week per Ernesto.

---

## Ticket #1 (Orig #5): Edit Order Confirm fails with same-day duplicate toast
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Mill Admin (https://admin.feedx.ag/order-management -> Edit Order modal)
- **The Issue:** When Mill Admin opens Edit Order on the 10/23/2026 Pending Cornmeal row, the -1 day bug shifts Delivery Date to 10/22/2026 (where a Confirmed Cornmeal order already exists). Clicking Confirm fails with red toast: 'Cannot have multiple orders of the same product on the same day.'
- **Expected:** Admin can confirm or edit the 10/23/2026 order without a false date collision on 10/22/2026.
- **Actual:** Red toast 'Cannot have multiple orders of the same product on the same day.' blocks saving.
- **Repro Steps:**
  1. In Mill Admin /order-management?statuses=PENDING, find Cornmeal row Scheduled Delivery Date = 10/23/2026 (10 Tons).
  2. Click the pencil Edit icon (modal opens with Delivery Date = 10/22/2026).
  3. Click Confirm inside the modal.
- **Screenshots:** `def07_1_before_pending_1023.png` (Before: Pending Row 10/23/2026), `def07_2_input_staged_modal.png` (During: Modal Shifted to 10/22/2026), `def07_3_reaction_red_toast.png` (Reaction: Red Duplicate Error Toast), `def07_4_after_cancel_unchanged.png` (After: Modal Closed Unchanged)

---

## Ticket #2 (Orig #7): Farm Home Alerts contradict schedule-order dates and remaining days
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Farm Owner (/home Alerts vs. /schedule-order) & Mill Admin (/order-management?statuses=UNSCHEDULED)
- **The Issue:** On Farm Owner /home Alerts, Cornmeal displays 'Remaining Feed for 8 day(s) | Unscheduled | Next Delivery - 10/23/2026', whereas /schedule-order displays 'Remaining feed for 15 day(s) | Estimated Delivery - 10/30/2026' (and Mill Admin has zero 10/23/2026 Unscheduled Cornmeal row — 10/23 is Pending). Also, QA Kickoff Blend 10-14 has an active card on /schedule-order (11/10/2026, 26 days) but is missing from /home Alerts.
- **Expected:** /home Alerts and /schedule-order show the exact same next Unscheduled date and remaining days for every active feed.
- **Actual:** /home Alerts shows 10/23/2026 (8 days) for Cornmeal while /schedule-order shows 10/30/2026 (15 days).
- **Repro Steps:**
  1. Log in as Farm Owner and inspect Alerts on /home.
  2. Click Schedule Order (/schedule-order) and compare the dates and remaining days for Cornmeal and QA Kickoff Blend 10-14.
- **Screenshots:** `step5_1_after_fo_home_oct.png` (Home Alerts: Cornmeal Unscheduled 10/23 (8d)), `step5_6_after_fo_schedule_order.png` (Schedule Order: Cornmeal 10/30 (15d)), `step6_3_after_admin_unscheduled.png` (Admin Unscheduled: Earliest Cornmeal is 10/30)

---

## Ticket #3 (Orig #8): Weekend dates blocked for Farm Owner, enabled for Mill Admin
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Farm Owner (/schedule-order date picker) vs. Mill Admin (Edit Order modal & Unscheduled/Delivered rows)
- **The Issue:** Farm Owner /schedule-order disables all Saturdays and Sundays in the calendar popup, whereas Mill Admin Edit Order modal enables all Saturdays and Sundays, and Delivered/Unscheduled orders include Saturday (09/26/2026) and Sunday (10/18/2026, 11/29/2026) dates.
- **Expected:** Consistent weekend delivery rules across Farm Owner, Mill Admin, and auto-forecast generation.
- **Actual:** Farm Owner cannot select weekends, while Mill Admin and auto-forecast schedule on Saturdays and Sundays.
- **Repro Steps:**
  1. Open Farm Owner /schedule-order and click Delivery Date input: observe all Sat/Sun cells are disabled.
  2. Open Mill Admin /order-management, click Edit on any row, and click Delivery Date: observe all Sat/Sun cells are enabled.
- **Screenshots:** `obs03_step1_calendar_popup_oct.png` (Farm Date Picker: Sat/Sun Disabled), `hyp03_admin_edit_modal_calendar.png` (Admin Date Picker: Sat/Sun Enabled)

---

## Ticket #4 (Orig #10): Farm Owner direct calendar view route renders blank white screen
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Farm Owner (https://howlett.feedx.ag/orders/calendar/view)
- **The Issue:** Navigating directly to https://howlett.feedx.ag/orders/calendar/view renders a 100% blank white screen (empty root container).
- **Expected:** Renders the Farm Owner calendar view or redirects cleanly to /home.
- **Actual:** Renders a completely blank white screen.
- **Repro Steps:**
  1. While logged in as Farm Owner on howlett.feedx.ag, navigate to https://howlett.feedx.ag/orders/calendar/view.
- **Screenshots:** `def02_2_blank_calendar_view.png` (Farm /orders/calendar/view: Blank White Screen)

---

## Ticket #5 (Orig #11): Admin status filter on Page 2 shows false No data
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Mill Admin (https://admin.feedx.ag/order-management)
- **The Issue:** Changing the Status filter (e.g., from All to Confirmed) while on Page 2 does not reset page=1; it queries page=2&statuses=CONFIRMED and displays 'No data' with disabled '<' and '>' arrows even though Page 1 has 4 Confirmed rows.
- **Expected:** Changing Status filter resets pagination to Page 1 and displays the 4 Confirmed rows.
- **Actual:** Table stays on Page 2 and shows 'No data' until the user manually clicks page number '1'.
- **Repro Steps:**
  1. In Mill Admin /order-management?search=zzz+Test+QA, click Page 2 at the bottom right.
  2. Click the Status filter dropdown and select Confirmed.
- **Screenshots:** `def04_1_before_page2.png` (Before: On Page 2 (Status = All)), `def04_2_input_staged_dropdown.png` (During: Selecting Confirmed on Page 2), `def04_3_reaction_nodata_page2.png` (Reaction: False 'No data' on Page 2), `def04_4_after_page1_recovery.png` (After: Clicking Page 1 Recovers 4 Rows)

---

## Ticket #6 (Orig #12): Admin inline status change gives no toast or table refresh
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Mill Admin (https://admin.feedx.ag/order-management?statuses=PENDING)
- **The Issue:** Changing an order's inline Status dropdown from Pending to Confirmed shows zero toast message and leaves the row sitting inside the Pending-filtered table until the user reloads the page.
- **Expected:** Shows a confirmation toast and removes the Confirmed row from the Pending-filtered view.
- **Actual:** Zero toast appears and the row stays in the Pending table displaying 'Confirmed' until F5 reload.
- **Repro Steps:**
  1. In Mill Admin /order-management?statuses=PENDING, click the inline Status dropdown on a Pending row.
  2. Select Confirmed and observe the screen before reloading.
- **Screenshots:** `step2_1_before_pending_table.png` (Before: Pending Row 11/20/2026), `step2_2_input_staged_status_dropdown.png` (During: Inline Dropdown Open), `step2_3_reaction_silent_no_toast.png` (Reaction: No Toast, Row Still in Pending View), `step2_4_after_confirmed_table.png` (After Reload: Moved to Confirmed View)

---

## Ticket #7 (Orig #13): Admin Delivered rows still open editable Edit Order modal
- **Status / Priority:** Slated for Next Week (Hold Off DevOps Ticket Today)
- **Where:** Mill Admin (https://admin.feedx.ag/order-management?statuses=DELIVERED)
- **The Issue:** On Delivered rows, the inline Status dropdown is disabled, but the pencil Edit icon in the Action column remains clickable and opens a live Editing Order modal with an active green Confirm button.
- **Expected:** Pencil Edit icon is disabled or read-only for already Delivered orders.
- **Actual:** Opens a live Editing Order modal with editable inputs and an active Confirm button.
- **Repro Steps:**
  1. In Mill Admin /order-management?statuses=DELIVERED, scroll the table right to the Action column.
  2. Click the pencil Edit icon on Row 1 (Delivered).
- **Screenshots:** `hyp08_admin_delivered_right_cols.png` (Delivered Row: Status Disabled, Edit Active), `hyp08_2_delivered_edit_modal_open.png` (Clicked Edit: Live Editing Order Modal Opens)

---
