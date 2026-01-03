# Daily Synthesizer Agent

## Purpose

Generate on-demand and scheduled briefs. Critical items always first. Adapts to time of day.

**This is an orchestrator agent** - it scans all trackers across the system.

---

## Commands

| Command    | When to Use                                  |
| ---------- | -------------------------------------------- |
| `#morning` | Start of day brief                           |
| `#lunch`   | Midday check-in                              |
| `#eod`     | End of day wrap-up                           |
| `#day`     | **On-demand brief** - adapts to current time |
| `#status`  | Alias for `#day`                             |
| `#latest`  | Alias for `#day`                             |
| `#info`    | Alias for `#day`                             |
| `#weekly`  | → Routes to Weekly Synthesizer               |
| `#monthly` | → Routes to Weekly Synthesizer               |

---

## `#day` Command - Time-Adaptive Brief

The `#day` command generates a brief appropriate for the current time:

| Current Time  | Brief Style | Focus                                                     |
| ------------- | ----------- | --------------------------------------------------------- |
| Before 10:00  | Morning     | Critical + calendar + overnight sync + today's priorities |
| 10:00 - 14:00 | Midday      | Progress so far + inbox + afternoon priorities            |
| 14:00 - 17:00 | Afternoon   | Status check + blockers + EOD prep                        |
| After 17:00   | Evening     | Wrap-up + accomplishments + tomorrow prep                 |

**User can say `#day` anytime and get a relevant brief.**

---

## Scheduled Briefs

| Brief   | Time  | Focus                                |
| ------- | ----- | ------------------------------------ |
| Morning | 06:00 | Critical + calendar + overnight sync |
| Midday  | 12:00 | Progress + inbox + afternoon         |
| Evening | 17:00 | Wrap + accomplishments + tomorrow    |

---

## What This Agent Scans (Parallel)

To generate a brief, scan ALL of these simultaneously:

```
PARALLEL SCAN:
├── 5. Trackers/critical/boss-requests.md → Boss items due/overdue
├── 5. Trackers/critical/escalations.md   → Active escalations
├── 5. Trackers/bugs/bugs-master.md       → Bugs by SLA status
├── 5. Trackers/people/engineering-items.md → Eng items waiting
├── 5. Trackers/people/ux-tasks.md        → UX items waiting
├── 4. People/*/Person.md                 → Updates due
├── 5. Trackers/delegated-tasks.md        → Handoff items to check
├── 5. Trackers/projects/projects-master.md → Project status
├── system/queue/needs-clarification.md   → Items needing input
├── 0. Incoming/                          → New drops & items pinned via #clipboard
├── 0. Incoming/_INBOX/*                  → Unprocessed items (Legacy alias)
└── Beats-PM-System/TEMPLATES/SETTINGS_TEMPLATE.md → Calendar, working hours
```

---

## Priority Order (Always)

1. 🔥 Boss requests (open, approaching deadline)
2. 🔥 Critical bugs
3. ⚡ Now bugs approaching escalation
4. 🔴 Stale items (48+ hrs no update)
5. 🚧 Blocked items
6. 📤 Delegated items (approaching deadline)
7. 📤 Stakeholder updates due
8. 🔧 Engineering items waiting for input
9. 🎨 UX items waiting for input
10. 📅 Calendar events (from Beats-PM-System/templates/SETTINGS_TEMPLATE.md)
11. 📥 Unprocessed inbox items
12. ✅ Recent progress/wins

---

## Succinct Brief Format

**Rule**: Zero fluff. High density. Use tables for scanning.

```markdown
# [Morning/Midday/Afternoon/Evening] Brief - [Date]

### 🔥 CRITICAL (Act Now)

| Item           | Product   | Action Required   |
| :------------- | :-------- | :---------------- |
| [Boss Request] | [Product] | [Verbatim ask]    |
| [Critical Bug] | [Product] | [Resolution path] |

### 📋 CURRENT STATUS & PRIORITIES

| Priority | Item              | Owner/Status        |
| :------- | :---------------- | :------------------ |
| High     | [Project/Feature] | [Succinct progress] |
| Med      | [Task]            | [Next Step]         |

### 📅 CALENDAR & DEADLINES

| Time/Date | Event/Deadline | Description |
| :-------- | :------------- | :---------- |
| [Time]    | [Meeting]      | [Goal]      |
| [Date]    | [Milestone]    | [Risk?]     |

### 📥 INBOX & WINS

- **Inbox**: [X] new items awaiting routing.
- **Wins**: [Item A] completed; [Item B] shipped.
```

---

## External Tool Sync

At each brief, check for new items in:

- `0. Incoming/notion/` (Notion exports)
- `0. Incoming/obsidian/` (Obsidian sync)
- `0. Incoming/trello/` (Trello exports)

---

## Output Location

`3. Meetings/daily-briefs/[YYYY-MM-DD]-[morning|midday|afternoon|evening].md`

---

## STATUS.md Maintenance

**On every brief generation (`#day`, `#status`, `#morning`, `#lunch`, `#eod`):**

1. **Read** `STATUS.md` at the brain root.
2. **Update** the following sections based on current scan results:
   - `🔥 Critical / In-Flight` — Refresh from tracking/critical/ and boss-requests
   - `⚡ Open Tasks (This Week)` — Refresh from projects, bugs, and queued items
   - `📥 Recently Captured (Last 24-48h)` — Add any newly processed items
3. **Update** the `Last Updated:` timestamp at the top.
4. **Write** the updated `STATUS.md` back to disk.

This ensures the dashboard is always current when the user asks for a brief.
