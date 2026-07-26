---
title: Personal Memory Companion
description: Safely add optional local semantic recall to Beats PM Kit without replacing canonical Markdown evidence.
---

# Personal Memory Companion

Beats PM Kit can use [IAI Personal Memory Engine](https://github.com/CodeAbra/iai-personal-memory-engine) as an optional local recall companion. This is an accelerator, not a new source of truth: tasks, decisions, meeting evidence, and workstream state remain in human-readable Markdown.

## Why It Is Optional

IAI is a separate local application. Its current upstream package expects Python 3.11 or 3.12, Node.js 18+, Rust, a native build, and its own storage. Windows support is currently beta. Beats PM Kit does not install, vendor, start, update, or configure that software automatically.

The adapter uses only the local `iai` CLI. It does not call `iai ask`, install hooks, upload files, or invoke a cloud evaluation service. The companion is disabled unless you create the ignored local config through an explicit command.

## Privacy And Trust Boundary

- Config and backups stay under ignored `.beats/`.
- The external memory database stays in IAI's own local store; it is never copied into this repository.
- Recall and capture run as argument-list subprocesses with no shell and a bounded timeout.
- Failures return a small status code without echoing the private cue or captured text.
- Recalled content is labelled untrusted. Verify important claims against dated local Markdown before acting.
- Capture requires a second, separate opt-in.
- Recall cues are capped at 1,000 characters and curated captures at 4,000 characters to prevent accidental bulk ingestion.
- Do not capture raw transcripts, whole chat exports, secrets, credentials, hidden instructions, payment data, personal contact details, or sensitive health information.
- Your chosen AI runtime may still process tool output according to that provider's account and data settings.

## Check Status

```bash
python system/scripts/personal_memory.py status --json
```

With the universal gateway:

```bash
python system/scripts/beats.py personal-memory
```

No executable is probed while the companion is disabled.

## Enable Read-Only Recall

Install and validate IAI separately by following its official documentation. Then enable only the Beats adapter:

```bash
python system/scripts/personal_memory.py configure --enable --json
```

Use a dedicated local store when you want strict separation from memories used by other projects:

```bash
python system/scripts/personal_memory.py configure --enable --store "C:\path\to\private\beats-memory" --json
```

The config is backed up before every change.

## Recall With Deterministic Fallback

```bash
python system/scripts/personal_memory.py recall "What did we decide about the launch date?" --limit 5 --json
```

When IAI is disabled, missing, slow, unhealthy, or returns malformed output, the command degrades to `rg` without blocking the workflow. Run `/find` to search meeting transcripts, chat archives, decisions, tasks, and product documents.

## Enable Curated Capture

Capture stays blocked until you explicitly enable it:

```bash
python system/scripts/personal_memory.py configure --enable --enable-capture --json
```

Capture one short durable fact or decision, including its date and Markdown source:

```bash
python system/scripts/personal_memory.py capture "2026-07-26: Launch moved to Friday. Source: 3. Meetings/launch-review.md" --session-id "beats-launch" --json
```

This does not change the source Markdown and must not be used as an automatic dual-write path.

## Disable Or Reset

Disable while preserving explicit settings:

```bash
python system/scripts/personal_memory.py configure --disable --json
```

Back up and remove the local adapter config:

```bash
python system/scripts/personal_memory.py reset --json
```

Neither action deletes or changes IAI's external store.

## Upgrade Safety

`upgrade_compat.py` validates the ignored local adapter config before an upgrade proceeds. Valid settings are preserved exactly. Unknown schemas or malformed JSON block the upgrade with a repair message; the upgrade never guesses at a migration or touches the external memory database.
