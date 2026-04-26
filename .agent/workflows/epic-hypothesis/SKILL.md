---
name: epic-hypothesis
description: Frame an epic as a testable hypothesis with target user, expected outcome, and validation method. Use when defining a major initiative before roadmap, discovery, or delivery planning.
---

## Purpose
Frame epics as testable hypotheses using an if/then structure that articulates the action or solution, the target beneficiary, the expected outcome, and how you'll validate success. Use this to manage uncertainty in product development by making assumptions explicit, defining lightweight experiments ("tiny acts of discovery"), and establishing measurable success criteria before committing to full build-out.

This is not a requirements spec—it's a hypothesis you're testing, not a feature you're committed to shipping.

## Key Concepts

### The Epic Hypothesis Framework
Inspired by Tim Herbig's Lean UX hypothesis format, the structure is:

**If/Then Hypothesis:**
- **If we** [action or solution on behalf of target persona]
- **for** [target persona]
- **Then we will** [attain or achieve a desirable outcome or job-to-be-done]

**Tiny Acts of Discovery Experiments:**
- **We will test our assumption by:**
  - [Experiment 1]
  - [Experiment 2]
  - [Add more as necessary]

**Validation Measures:**
- **We know our hypothesis is valid if within** [timeframe]
- **we observe:**
  - [Quantitative measurable outcome]
  - [Qualitative measurable outcome]
  - [Add more as necessary]

### Why This Structure Works
- **Hypothesis-driven:** Forces you to state what you believe (and could be wrong about)
- **Outcome-focused:** "Then we will" emphasizes user benefit, not feature output
- **Experiment-first:** Encourages lightweight validation before full build
- **Falsifiable:** Clear success criteria make it possible to kill bad ideas early
- **Risk management:** Treats epics as bets, not commitments

### Anti-Patterns (What This Is NOT)
- **Not a feature spec:** "Build a dashboard with 5 charts" is a feature, not a hypothesis
- **Not a guaranteed commitment:** Hypotheses can (and should) be invalidated
- **Not output-focused:** "Ship feature X by Q2" misses the point—did it achieve the outcome?
- **Not experiment-free:** If you skip experiments and go straight to build, you're not testing a hypothesis

### When to Use This
- Early-stage feature exploration (before committing to full roadmap)
- Validating product-market fit for new capabilities
- Prioritizing backlog (epics with validated hypotheses get higher priority)
- Managing stakeholder expectations (frame work as experiments, not promises)

### When NOT to Use This
- For well-validated features (if you've already proven demand, skip straight to user stories)
- For trivial features (don't over-engineer small tweaks)
- When experiments aren't feasible (rare, but sometimes you must commit before testing)

---


## Application

This skill uses a structured 6-step process to frame epics as testable hypotheses. The complete step-by-step guide, experiment types, validation criteria, and common pitfalls are defined in `assets/hypothesis-guide.md`.

**Action:** Load `assets/hypothesis-guide.md` for the full application walkthrough and examples.

## Examples

See `assets/hypothesis-guide.md` for worked examples and common pitfall patterns.

## References

### Related Skills
- `skills/problem-statement/SKILL.md` — Hypothesis should address a validated problem
- `skills/proto-persona/SKILL.md` — Defines the "for [persona]" section
- `skills/jobs-to-be-done/SKILL.md` — Informs the "then we will" outcome
- `skills/user-story/SKILL.md` — Validated epics decompose into user stories
- `skills/user-story-splitting/SKILL.md` — How to break validated epics into stories

### External Frameworks
- Tim Herbig, *Lean UX Hypothesis Statement* — Origin of if/then hypothesis format
- Jeff Gothelf & Josh Seiden, *Lean UX* (2013) — Hypothesis-driven product development
- Alberto Savoia, *Pretotype It* (2011) — Lightweight experiments to validate ideas
- Eric Ries, *The Lean Startup* (2011) — Build-Measure-Learn cycle

### Dean's Work
- Backlog Epic Hypothesis Prompt (inspired by Tim Herbig's framework)

### Provenance
- Adapted from `prompts/backlog-epic-hypothesis.md` in the `https://github.com/deanpeters/product-manager-prompts` repo.

---

**Skill type:** Component
**Suggested filename:** `epic-hypothesis.md`
**Suggested placement:** `/skills/components/`
**Dependencies:** References `skills/problem-statement/SKILL.md`, `skills/proto-persona/SKILL.md`, `skills/jobs-to-be-done/SKILL.md`
**Used by:** `skills/user-story/SKILL.md`, `skills/user-story-splitting/SKILL.md`
