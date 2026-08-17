# Proposal: Clickable Markdown Preview Links (Pi / Oh My Pi / Orca)

Make every markdown file the kit generates or references one click away for the user: emit a `file://` hyperlink that the host app can actually render, and auto-open key deliverables in a new browser tab when the runtime supports it.

> Status: Approved 2026-08-17 (Ernesto)
> Owner: Ernesto Rodriguez
> Target: beats-pm-kit core (officebeats/beats-pm-kit)

## Problem

1. Agents reference vault files by relative path; users must locate them manually.
2. Vaults commonly live in iCloud Drive (`~/Library/Mobile Documents/...`). Sandboxed webviews (Orca's embedded browser, and likely other Electron-class hosts) cannot read those paths — `file://` links to them render a **white screen** even though the file is fine. Verified 2026-08-17: identical content served from `/tmp` displays correctly.
3. There is no kit-standard way to open a deliverable for the user, so each agent improvises (HTML renders, raw paths, nothing).

## Design

### 1. `system/scripts/preview_link.py` (new)

Single entry point for "give the user a clickable view of this file":

- `preview_link.py <path> [--open] [--json]`
- Stages a copy in a webview-readable dir: `${TMPDIR}/beats-pm-preview/<flattened-vault-relative-path>`. Staging is copy-on-call, so the link always reflects the latest saved version; re-running refreshes it.
- Prints the percent-encoded `file://` URL. `--json` returns `{source, staged, url, opened}`.
- `--open`: if an Orca CLI is detected (`ORCA_CLI_COMMAND`, `orca-dev`, `orca-ide`, `orca` per Orca's resolution rules), run `<cli> tab create --url <url> --json`; otherwise fall back to `open`/`xdg-open`; otherwise print the URL only. Never fail the calling workflow because open failed.
- Skip staging when the source path is already webview-readable (not under `Mobile Documents`) — link the original directly so edits show on reload.

### 2. Adapter/runtime integration

- **AGENTS.md rule**: whenever a workflow generates or cites a markdown deliverable in a user-facing response, include the `preview_link.py` URL as a clickable link; auto-`--open` only for primary deliverables, never for bulk references.
- **Workflows**: `/plan`, `/create`, `/deck`, `/track`, `/week`, `/boss`, `/review` output steps append the preview link.
- **`.agent/rules/ACTION_FIRST_OUTPUT.md`**: deliverable mentions carry their clickable link.

### 3. Hygiene

- Staged copies are throwaway: `/vacuum` clears the preview dir; it is never a source of truth and never synced back.
- Privacy: staging stays on-device under the user tmpdir; no network, no artifact publishing.

## Non-goals

- No HTML rendering pipeline (raw markdown in the host viewer is the contract; Obsidian remains the rich viewer).
- No source-system writes; no changes to canonical note storage.

## Verification

- iCloud vault: generate a doc, click the emitted link in Orca → content visible in new tab.
- Non-iCloud vault: link points at the original file (no staging copy).
- No Orca CLI present: prints a usable URL, exits 0.

## PM Bar

- **Outcome metric**: every deliverable mention is one click from viewable; zero white-screen reports.
- **Scope boundary**: link emission + optional open only; no viewer, no sync, no publishing.
- **Evidence strength**: strong — white-screen root cause reproduced and fix verified live (2026-08-17, Orca 1.4.183, macOS 15/25.6).
- **Dependencies**: Orca CLI resolution rules; tmpdir semantics per OS.
- **Next decision gate**: implemented → PR to officebeats/beats-pm-kit main.
