---
description: Orchestrate and track PI Planning activities for Ascension's 3-day format.
---

# 🏗️ PI Planning Playbook (`/pi`)

This workflow guides the PM through Ascension's 3-day Program Increment Planning ceremony.

## Ascension PI Format
- **Day 1**: Vision & Draft Plans
- **Day 2**: Pre-Read (Team Refinement & Breakouts)
- **Day 3**: Final Read (Commit, Vote, Risk Review)

---

## Step 1: Pre-PI Prep (Before Day 1)
Before you enter the room, ensure the following:
- [ ] **Gabriel Mandates Confirmed**: Have you synced with leadership on top priorities?
- [ ] **Backlog Pre-Baked**: Top features and stories drafted; not discovering from scratch.
- [ ] **Risks Identified**: Known blockers (e.g., Salesforce/R1 parity) documented.
- [ ] **Architect Pre-Sync**: Critical architecture questions answered beforehand.

**Action**: If you haven't done this, run `/prep [PI Planning]` to generate a 30-second cheat sheet.

---

## Step 2: Day 1 - Vision & Draft Plans
**Your PM Responsibilities**:
- [ ] Attend Vision & Leadership Deck session.
- [ ] Break out with your team to draft **Iteration Plans** (Sprint 1-4 scope).
- [ ] Sanity-check **Capacity**: Account for PTO, holidays, and the 13-point PI placeholder.
- [ ] Identify **Discovery vs. Delivery** split (e.g., Pre-Reg = Discovery, Messaging = Delivery).

**Tip**: Capture any new asks or scope changes in a "Parking Lot" list.

---

## Step 3: Day 2 - Pre-Read (Refinement & Breakouts)
**Your PM Responsibilities**:
- [ ] Review and refine **Iteration Plans** with the team.
- [ ] Participate in **Breakout Sessions** for cross-team dependency alignment.
- [ ] Prepare **PI Objectives** (What are you committing to deliver?).
- [ ] Surface **Dependencies** on the Program Board (e.g., "Need Salesforce API by Sprint 2").

**Tip**: Use this day to pressure-test your plan. If you have a blocker, call it out now.

---

## Step 4: Day 3 - Final Read (Commit & Vote)
**Your PM Responsibilities**:
- [ ] Finalize **PI Objectives** and present during the Final Read.
- [ ] Participate in the **Program Board** review (cross-team milestones).
- [ ] Engage in **ROAM Session**: Surface risks (Resolved, Owned, Accepted, Mitigated).
- [ ] Cast your **Confidence Vote** (1-5 fingers). If team average < 3, re-plan.
- [ ] Capture all **Commitments** made during discussions.

**Output**: Locked PI plan with clear sprint objectives, identified risks, and dependencies called out.

---

## Step 5: Post-PI Sync
After the session:
- [ ] Update `5. Trackers/PROJECT_TRACKER.md` with new PI scope.
- [ ] Update `BOSS_REQUESTS.md` if any new mandates emerged.
- [ ] Schedule **Discovery Exit Checkpoints** for discovery work (Pre-Reg, Steering Agent).

---

## Quick Reference: PM Superpowers
- **Be the Context Synthesizer**: Have your Cheat Sheet ready (`/prep [PI Planning]`).
- **Guard Scope Creep**: New requests → Backlog for next PI.
- **Set Exit Objectives**: For discovery work, define what "done" looks like per sprint.
- **Capture Decisions**: Write down commitments in real-time.

---

## Trigger
When the user mentions "PI planning" or "PI prep", this workflow activates and tracks progress against the above checklist.
