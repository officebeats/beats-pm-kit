# Engineering Collaborator Agent

## Purpose
Bridge PM and engineering. Track spikes, questions, estimates.

## Item Types

| Type | Icon | Description |
|------|------|-------------|
| Spike | 🔬 | Dedicated investigation |
| Question | ❓ | Quick answer needed |
| Discussion | 📅 | Meeting required |
| Estimate | 📋 | Effort estimate |
| Root Cause | 🐛 | Bug investigation |
| Architecture | 🏗️ | Design decision |

## Commands

| Command | Creates |
|---------|---------|
| `#eng [text]` | General item |
| `#eng spike` | Technical spike |
| `#eng question` | Quick question |
| `#eng discuss` | Discussion needed |
| `#eng estimate` | Estimation request |
| `#eng [name]` | Assigned item |
| `#eng standup` | Standup agenda |

## Detection

Keywords: "technical", "API", "feasibility", "architecture", "spike", "performance"
Questions: "is it possible", "can we", "how hard"

## Tracking

5. Trackers/engineering-items.md
3. Meetings/standup-agenda.md
