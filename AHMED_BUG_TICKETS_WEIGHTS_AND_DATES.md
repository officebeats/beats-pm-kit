# FeedX Today's Bug Pack for Ahmed (7 Active DevOps Tickets)

> Approved for DevOps Ticket Creation Today. (7 additional tickets — Orig #5, #7, #8, #10, #11, #12, #13 — are held off for next week in FEEDX_NEXT_WEEK_DEFERRED_BUGS.md / .html).

---

## Ticket #1 (Orig #1): Driver weight rounds to 20-lb increments and confuses Pounds with Tons
- **Status / Priority:** P1 - Today (Weight & Unit Mismatch)
- **Where:** Driver (/truck-driver/home & /truck-driver/delivery-history), Farm Owner (/order-history & /my-feeds), Mill Admin (/order-management)
- **The Issue:** Driver enters weight in Pounds while Farm Owner and Mill Admin display Tons (2 decimal places). Entering 777 lbs rounds to 780 lbs (+3 lbs) in Driver History and 0.39 Tons in Farm/Admin. Entering 24.5 (thinking the input is Tons) records 20 lbs in Driver History and 0.01 Tons in Farm/Admin.
- **Expected:** Preserve exact driver weight (777 lbs) without 20-lb rounding, and show Weight Ordered (Tons) plus a live Tons conversion in the Driver modal.
- **Actual:** 777 lbs becomes 780 lbs (0.39 Tons); 24.5 becomes 20 lbs (0.01 Tons).
- **Repro Steps:**
  1. Log in as Driver (qaernestodriver@yopmail.com), search zzz Test QA FARM (Ernesto), click Confirm Delivery.
  2. Enter 777 in Weight Delivered (Pounds), click Proceed (shows 777 Pounds), then click Confirm.
  3. Compare Driver Delivery History Page 1 Rows 2-3 (780 lbs) against Farm Owner /order-history Page 2 Rows 12 & 16 (0.39 Tons) and Mill Admin Delivered (Ordered: 24 | Delivered: 0.39).
- **Screenshots:** `def09_3_confirm_summary_777_lbs.png` (Driver Modal: 777 Pounds Entered), `step3_4_after_driver_history.png` (Driver History: Rounded to 780 & 20 lbs), `step4_2_after_fo_history_page2.png` (Farm History Page 2: 0.39 Tons), `step6_2_after_admin_delivered.png` (Admin Delivered: 0.39 & 0.01 Tons)

---

## Ticket #2 (Orig #2): Schedule cards show Last Delivery Date: N/A and wrong Previous Amount Requested
- **Status / Priority:** P1 - Today (Missing Date & Wrong Weight on Card)
- **Where:** Farm Owner (/schedule-order vs. /my-feeds & /order-history) for zzz Test QA FARM (Ernesto)
- **The Issue:** On /schedule-order, Cornmeal shows Last Delivery Date: N/A | Previous Amount Requested: 10 Tons (and SSO Test shows N/A | 5 Tons), even though /my-feeds shows Last Delivery Date: 10/14/2026 | Weight Delivered: 24.5 Tons for Cornmeal and 10/13/2026 | 15 Tons for SSO Test.
- **Expected:** Schedule cards display Last Delivery Date = 10/14/2026 (Cornmeal) / 10/13/2026 (SSO Test) and actual last weight.
- **Actual:** Both cards display Last Delivery Date: N/A, and Previous Amount Requested shows the unscheduled forecast row's weight (10 Tons / 5 Tons) instead of the last order.
- **Repro Steps:**
  1. Log in as Farm Owner (qaernestofarmowner@yopmail.com) and open /my-feeds: verify Cornmeal Last Delivery Date = 10/14/2026, Weight Delivered = 24.5 Tons.
  2. Click Schedule Order (/schedule-order) and inspect the Cornmeal and SSO Test cards.
- **Screenshots:** `step5_5_after_fo_my_feeds.png` (My Feeds: 10/14/2026 | 24.5 Tons), `step5_6_after_fo_schedule_order.png` (Schedule Order: Last Delivery N/A | 10 Tons), `step0_admin_unscheduled.png` (Admin Unscheduled Page 1: Last Delivery N/A)

---

## Ticket #3 (Orig #3): Remaining feed days ignore weight math and Feeding Rate changes
- **Status / Priority:** P1 - Today (Forecast Math & Rate Input Ignored)
- **Where:** Farm Owner (/schedule-order)
- **The Issue:** Cornmeal shows 10 Tons at 5 Tons/day (2 days of feed) or 24.5 Tons delivered (4.9 days), yet displays Remaining feed for 15 day(s) (10/30 - 10/15). Changing Feeding Rate from 5 to 10 Tons/day does not recalculate Remaining feed for 15 day(s) or Estimated Delivery - 10/30/2026.
- **Expected:** Doubling Feeding Rate from 5 to 10 Tons/day halves remaining feed days and moves Estimated Delivery earlier.
- **Actual:** Neither Remaining feed for 15 day(s) nor Estimated Delivery - 10/30/2026 changes.
- **Repro Steps:**
  1. Open Farm Owner /schedule-order and locate Cornmeal (QA Test) Ernesto.
  2. Change Feeding Rate from 5 to 10 Tons/day.
  3. Observe Remaining feed for 15 day(s) and Estimated Delivery - 10/30/2026.
- **Screenshots:** `step5_6_after_fo_schedule_order.png` (Before: Rate = 5, 15 days, 10/30/2026), `hyp01_2_input_staged_feeding_rate_10.png` (During: Rate = 10, still 15 days & 10/30/2026), `hyp01_4_after_restored_rate_5.png` (After: Restored Rate = 5)

---

## Ticket #4 (Orig #4): Admin Edit Order modal shifts Delivery Date back one day
- **Status / Priority:** P1 - Today (Date Shifted -1 Day on Edit)
- **Where:** Mill Admin (https://admin.feedx.ag/order-management -> Edit Order modal)
- **The Issue:** Clicking the pencil Edit icon on any order row in America/Chicago (UTC-5) pre-fills the modal's Delivery Date 1 day earlier than the table row's Scheduled Delivery Date (11/20/2026 becomes 11/19/2026; 10/23/2026 becomes 10/22/2026).
- **Expected:** Modal Delivery Date pre-fills 11/20/2026 (or 10/23/2026) matching the table row.
- **Actual:** Modal Delivery Date pre-fills 11/19/2026 (or 10/22/2026) — 1 day earlier.
- **Repro Steps:**
  1. In Mill Admin /order-management (America/Chicago UTC-5), filter zzz Test QA FARM (Ernesto) and Status = Pending.
  2. Verify row Scheduled Delivery Date = 11/20/2026 (or 10/23/2026) in the table.
  3. Click the pencil Edit icon on that row and read Delivery Date inside the modal.
- **Screenshots:** `def03_1_before_row_1120.png` (Table Row: Scheduled 11/20/2026), `def03_2_modal_during_1119_shift.png` (Edit Modal: Pre-filled 11/19/2026 (-1 Day)), `def07_2_input_staged_modal.png` (10/23 Row Modal: Pre-filled 10/22/2026 (-1 Day))

---

## Ticket #5 (Orig #6): Farm Order History scatters today's deliveries across Pages 1 and 2
- **Status / Priority:** P1 - Today (Cross-Role Delivery Date & Sort Mismatch)
- **Where:** Driver (/truck-driver/delivery-history) vs. Farm Owner (/order-history) vs. Mill Admin (/order-management?statuses=DELIVERED)
- **The Issue:** Driver Confirm Delivery locks Delivery Date to today (10/14/2026) and Driver History puts all four 10/14/2026 deliveries at Page 1 Rows 1-4. Farm Owner /order-history hides Scheduled Delivery Date and displays only Last Delivery Date in non-chronological order (matching Mill Admin Delivered row order, where 11/05 & 11/04 precede 12/02 and 10/22 is on Page 2 after 10/09 on Page 1), scattering the four 10/14/2026 deliveries to Page 1 Rows 5 & 7 and Page 2 Rows 12 & 16.
- **Expected:** Farm Owner /order-history sorts chronologically by Last Delivery Date DESC (putting 10/14/2026 at Rows 1-4) and displays Scheduled Delivery Date alongside Last Delivery Date.
- **Actual:** 10/14/2026 deliveries are buried at Page 1 Rows 5 & 7 (under 10/11 rows) and Page 2 Rows 12 & 16.
- **Repro Steps:**
  1. Open Driver /truck-driver/delivery-history Page 1: see all four 10/14/2026 deliveries at Rows 1-4 (49,000, 780, 780, 20 lbs).
  2. Open Farm Owner /order-history Page 1 & Page 2: look for the four 10/14/2026 deliveries.
  3. Compare with Mill Admin /order-management?statuses=DELIVERED (which shows both Last Delivery Date = 10/14/2026 and Scheduled Delivery Date = 11/20, 10/23, 10/20, 09/26).
- **Screenshots:** `step3_4_after_driver_history.png` (Driver Page 1: 10/14 Deliveries at Rows 1-4), `step4_1_after_fo_history_unfiltered.png` (Farm Page 1: 10/14 at Rows 5 & 7), `step4_2_after_fo_history_page2.png` (Farm Page 2: 10/14 at Rows 12 & 16), `step6_2_after_admin_delivered.png` (Admin Delivered: Shows Both Dates)

---

## Ticket #6 (Orig #9): Active Canola Meal missing from Farm schedule-order screen
- **Status / Priority:** P2 - Today (Missing Reorder Card)
- **Where:** Farm Owner (/schedule-order vs. /my-feeds) & Mill Admin (/product-management & /order-management)
- **The Issue:** Canola Meal is ACTIVE in Mill Admin Product Management, listed on Farm Owner /my-feeds (Last Delivery Date: 10/11/2026 | 24 Tons), and has two Unscheduled rows in Mill Admin (12/29/2026 on Page 2 Row 9 and 01/18/2027 on Page 1 Row 17), but renders zero card on /schedule-order.
- **Expected:** Canola Meal either renders a schedule card or shows why its next unscheduled load (12/29/2026) is hidden.
- **Actual:** Only 3 cards render (SSO Test, Cornmeal, QA Kickoff Blend 10-14); Canola Meal is completely absent.
- **Repro Steps:**
  1. Verify Canola Meal is active on Farm Owner /my-feeds and has Unscheduled rows on 12/29/2026 & 01/18/2027 in Mill Admin.
  2. Open Farm Owner /schedule-order and look for Canola Meal.
- **Screenshots:** `step0_1_product_mgmt.png` (Admin Product Mgmt: Canola Active), `step0_admin_unscheduled_page2.png` (Admin Unscheduled Page 2: Canola 12/29/2026), `step5_5_after_fo_my_feeds.png` (Farm My Feeds: Canola Listed), `step5_6_after_fo_schedule_order.png` (Farm Schedule Order: Canola Missing)

---

## Ticket #7 (Orig #14): Admin Calendar page renders zero orders across October
- **Status / Priority:** P2 - Today (Empty Calendar View)
- **Where:** Mill Admin (https://admin.feedx.ag/calendar)
- **The Issue:** Clicking Calendar in the Mill Admin left sidebar renders an empty October 2026 calendar grid with zero order chips, despite 71 orders (16 Delivered, 6 Pending, 4 Confirmed, 45 Unscheduled) in /order-management.
- **Expected:** October 2026 calendar displays scheduled/confirmed/delivered orders.
- **Actual:** Every day cell in October 2026 is completely empty.
- **Repro Steps:**
  1. Log in to Mill Admin (https://admin.feedx.ag) and click Calendar in the left navigation.
- **Screenshots:** `hyp04_1_admin_calendar.png` (Admin /calendar: Empty October 2026 Grid)

---
