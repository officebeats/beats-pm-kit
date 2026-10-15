# MUSE AGENT AUTOMATED TESTING & EXECUTION GUIDE: FEEDX QUALITY SUITE

> **Target Environment:** `https://admin.feedx.ag`  
> **Commercial Tenant:** Howlett Farms (`howlett`)  
> **Authoritative Test Matrix:** `system/qa/feedx_test_matrix.py` (51 Scenarios)  
> **Master Report Output:** `feedx_qa_execution_report.html` and OneDrive Sync


> **ERNESTO DIRECTIVE FOR MUSE & CLAUDE AGENTS (2026-10-15 — TODAY vs. NEXT WEEK BUG SPLIT):**
> - **Today's Active DevOps Bug Pack (7 Tickets — Create Today):** See [`AHMED_BUG_TICKETS_WEIGHTS_AND_DATES.md`](AHMED_BUG_TICKETS_WEIGHTS_AND_DATES.md) and [`AHMED_BUG_TICKETS_FOR_AHMED.html`](AHMED_BUG_TICKETS_FOR_AHMED.html):
>   1. Driver weight rounds to 20-lb increments and confuses Pounds with Tons.
>   2. Schedule cards show `Last Delivery Date: N/A` and wrong `Previous Amount Requested`.
>   3. Remaining feed days ignore weight math and `Feeding Rate` changes.
>   4. Admin `Edit Order` modal shifts `Delivery Date` back one day.
>   5. Farm `Order History` scatters today's deliveries across Pages 1 and 2.
>   6. Active `Canola Meal` missing from Farm `schedule-order` screen.
>   7. Admin `Calendar` page renders zero orders across October.
> - **Held Off for Next Week (7 Tickets — DO NOT Create DevOps Tickets Today):** See [`FEEDX_NEXT_WEEK_DEFERRED_BUGS.md`](FEEDX_NEXT_WEEK_DEFERRED_BUGS.md) and [`FEEDX_NEXT_WEEK_DEFERRED_BUGS.html`](FEEDX_NEXT_WEEK_DEFERRED_BUGS.html):
>   1. `Edit Order` Confirm fails with same-day duplicate toast (Orig #5).
>   2. Farm `Home Alerts` contradict `schedule-order` dates and remaining days (Orig #7).
>   3. Weekend dates blocked for Farm Owner, enabled for Mill Admin (Orig #8).
>   4. Farm Owner direct calendar view route (`/orders/calendar/view`) renders blank white screen (Orig #10).
>   5. Admin status filter on Page 2 shows false `"No data"` (Orig #11).
>   6. Admin inline status change gives no toast or table refresh (Orig #12).
>   7. Admin `Delivered` rows still open editable `Edit Order` modal (Orig #13).
---

## 1. Test Accounts & Persona Authentication Registry

The FeedX test suite exercises 5 distinct personas. Each persona has specific permissions and boundaries:

| Persona Role | Account Name | Email Address | Access Level & Scope |
| :--- | :--- | :--- | :--- |
| **Mill Admin / Dispatcher** | Ernesto Rodriguez | `rodriguez.ernesto@captiospartners.com` | Full dispatch, order management, price catalog, and calendar controls. |
| **Consulting Nutritionist** | QA Test Nitritionist (Ernesto) | `qaernesto@yopmail.com` | Linked to farm `zzz Test QA`; submits custom mixes and attaches formulation PDFs. |
| **Farm Owner** | QA Test Farm Owner (Ernesto) | `qaernestofarmowner@yopmail.com` | Silo inventory overview, depletion countdowns, and reorder requests. |
| **Barn Feeder** | QA Test Feeder (Ernesto) | `qaernestofeeder@yopmail.com` | Routine reorders allowed when `canManageOrders` toggle is active. |
| **Truck Driver** | QA Test (Ernesto) | `qa-driver@feedx.test` | Delivery manifests, proximity check-in, and net scale weight logging. |

### How Authentication Works in the Muse VM
Authentication on `admin.feedx.ag` is stored in browser `localStorage`. To authenticate any Playwright browser session without handling 2FA prompts:

```python
# Inject saved session token into browser localStorage
page.goto("https://admin.feedx.ag")
page.evaluate(f"localStorage.setItem('token', '{TOKEN}')")
page.goto("https://admin.feedx.ag/overview")
```

The active JWT token is stored locally in `temp_token.txt`.

---

## 2. Environment Setup inside the Muse VM

Run these terminal commands in the root of the repository:

```bash
# 1. Install Playwright and browser dependencies
pip install playwright openpyxl pandas
playwright install msedge chromium

# 2. Verify token presence
python -c "assert open('temp_token.txt').read().strip(), 'Token missing!'"
```

---

## 3. Running Automated Tests in Muse VM

### Option A: Run the 7 Critical Core Focus Scenarios (2.5 Minutes)
Executes Calendar maintenance lockout, alerts, consolidated schedule orders, nutritionist delegation, delivered delivered weights, multi-farm isolation, and mobile iPhone 14 parity:

```bash
python system/qa/run_comprehensive_7_suite.py
```

### Option B: Run the Full 51-Scenario Regression Suite (~4 Minutes)
Runs the entire master test matrix across all 18 modules:

```bash
python system/qa/run_full_51_suite.py
python system/qa/enrich_results.py
```

---

## 4. Generating the Interactive Report

After running tests, compile the visual HTML report with the top video strip and the new Excel summary table tab:

```bash
python system/qa/generate_clean_layman_report.py
```

### Where the Outputs Are Saved:
1. **Local Working File:** `feedx_qa_execution_report.html` (opens directly in Edge/Chrome).
2. **Timestamped Archive:** `system/qa/runs/feedx_qa_report_YYYY-MM-DD_HHMMSS.html`.
3. **OneDrive Sync Folder:** `C:\Users\ErnestoRodriguez\OneDrive - Captios Partners\FeedX_QA_Reports\FeedX_QA_Report_Latest.html`.

---

## 5. Defect Logging Standard (Unslop & Layman Rules)

When adding or asserting new test scenarios, Muse agents must follow the repository's plain-language reporting rules:
* **No AI filler words:** Do not use `delve`, `leverage`, `streamline`, `robust`, `foster`, or `empower`.
* **No vague jargon:** Avoid abstract terms like "reconciliation." Use descriptive actions (e.g., *"order row stays stuck on screen instead of disappearing"*).
* **Format for Every Finding:**
  1. **What is tested:** The exact button, modal, or input touched.
  2. **Why it matters:** Operational consequence to mill dispatchers or dairy farmers.
  3. **How it was tested:** Exact step sequence.
  4. **Photographic proof:** Before, during, and after screenshots.
  5. **Observed result:** Plain statement of what happened on screen.
