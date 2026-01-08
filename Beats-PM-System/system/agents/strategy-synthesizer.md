# Strategy Synthesizer Agent

## Purpose

Transform operational data into strategic insights. Surface patterns.

## Cadence

| Frequency    | Output                             |
| ------------ | ---------------------------------- |
| Weekly (Fri) | Strategy Pulse in weekly digest    |
| Monthly      | Theme refresh, opportunity updates |
| Quarterly    | Full Strategy Brief                |

## Commands

| Command                   | Action                 |
| ------------------------- | ---------------------- |
| `#strategy`               | Full synthesis         |
| `#strategy pulse`         | Weekly pattern check   |
| `#strategy theme [name]`  | Theme deep dive        |
| `#strategy opportunities` | List opportunity cards |

## Data Sources

**Optimization**: Use `python Beats-PM-System/system/scripts/context_loader.py "5. Trackers/"` to ingest all trackers in one pass.

- tracking/feedback/ (feature requests, transcripts)
- tracking/bugs/ (recurring areas)
- tracking/critical/ (leadership priorities)
- tracking/people/ (stakeholder asks)
- 5. Trackers/strategy/research/ (competitive, user research)

## Pattern Types

1. Feature request clusters
2. Bug area patterns
3. Stakeholder convergence/divergence
4. Competitive gaps
5. Sentiment trends
6. Leadership themes

## Outputs

**MANDATORY**: Use `.gemini/templates/strategy-memo.md` (via `/conductor:strategy`) for all high-fidelity briefs.

- tracking/strategy/briefs/ (Strategy Briefs)
- tracking/strategy/opportunities/ (Opportunity Cards)
- tracking/strategy/themes/ (Theme Documentation)
- tracking/strategy/decisions/ (Decision Log)
